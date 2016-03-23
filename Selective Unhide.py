# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy


bl_info = {
    "name": "Selective Unhide",
    "description": "Selectively unhide objects instead of unhiding all objects at once",
    "author": "Ray Mairlot",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "3D View> Alt + H",
    "category": "3D View"}



def getHiddenBones():
    
    return [bone for bone in bpy.context.active_object.data.edit_bones if bone.hide] 



def getHiddenBoneGroups():
    
    hiddenBones = getHiddenBones()
    
    hiddenBoneGroups = []
    
    armature = bpy.context.active_object
    
    for boneGroup in armature.pose.bone_groups:
        
        for hiddenBone in hiddenBones:
            
            if armature.pose.bones[hiddenBone.name].bone_group == boneGroup and boneGroup not in hiddenBoneGroups:
                
                hiddenBoneGroups.append(boneGroup)        
    
    return hiddenBoneGroups            



def getHiddenObjects():
    
    return [object for object in bpy.context.scene.objects if object.hide]



def getHiddenGroups():
    
    #Possible, but not very readable
    #hiddenGroups = [group.name for hiddenObject in hiddenObjects if hiddenObject.name in group.objects and group.name not in hiddenGroups]
    
    hiddenObjects = getHiddenObjects()
    
    hiddenGroups = []
                    
    for group in bpy.data.groups:
        
        for hiddenObject in hiddenObjects:

            if hiddenObject.name in group.objects and group not in hiddenGroups:
                
                hiddenGroups.append(group)
                
    return hiddenGroups
    


def getHiddenItems(scene, context):
    
    if bpy.context.mode == "OBJECT":
        
        hiddenGroups = [(item.name, item.name, "Group") for item in getHiddenGroups()]
        
        hiddenObjects = [(item.name, item.name, "Object") for item in getHiddenObjects()]

    elif bpy.context.mode == "EDIT_ARMATURE":
        
        hiddenGroups = [(item.name, item.name, "Bone Group") for item in getHiddenBoneGroups()]
        
        hiddenObjects = [(item.name, item.name, "Bone") for item in getHiddenBones()]

    return hiddenObjects + hiddenGroups



class UnhideSearch(bpy.types.Operator):
    """Search through a list of hidden items"""
    bl_idname = "object.unhide_search"
    bl_label = "Hidden Items"
    bl_property = "hiddenItems"

    hiddenItems = bpy.props.EnumProperty(name="Hidden Items", description="Holds a list of the hidden items", items=getHiddenItems)

    def execute(self, context):
        
        allHiddenItems = getHiddenItems(context.scene, context)
        
        for item in allHiddenItems:
            
            if item[0] == self.hiddenItems:
                
                itemType = item[2]
                                                  
        if bpy.context.mode == "OBJECT":
                
            bpy.ops.object.show(type=itemType, itemName=self.hiddenItems)
            
        elif bpy.context.mode == "EDIT_ARMATURE":
            
            bpy.ops.object.show(type=itemType, itemName=self.hiddenItems, armature=bpy.context.active_object.name)
            
            
        return {'FINISHED'}


    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}



class UnhideObject(bpy.types.Operator):
    """Unhide the object or group of objects"""
    bl_idname = "object.show"
    bl_label = "Show a specific object or group"
    bl_options = {"INTERNAL"}

    itemName = bpy.props.StringProperty()
    type = bpy.props.StringProperty()
    unHideAll = bpy.props.BoolProperty(default=False)
    armature = bpy.props.StringProperty()

    def execute(self, context):
        
        if self.type == "Object" and not self.unHideAll:
            
            bpy.data.objects[self.itemName].hide = False
            bpy.data.objects[self.itemName].select = True
            bpy.context.scene.objects.active = bpy.data.objects[self.itemName]
        
        elif self.unHideAll:
            
            for object in getHiddenObjects():
                                
                if object.type == self.itemName:
                    
                    object.hide = False
                    object.select = True
                    bpy.context.scene.objects.active = object
            
        elif self.type == "Group":
            
            for object in bpy.data.groups[self.itemName].objects:
                
                if object.hide:
                
                    object.hide = False
                    object.select = True
                    
        elif self.type == "Bone":
            
            armature = bpy.data.objects[self.armature].data
            armature.edit_bones[self.itemName].hide = False
            armature.edit_bones[self.itemName].select = True
            armature.edit_bones.active = armature.edit_bones[self.itemName]
            
        elif self.type == "Bone Group":
            
            armature = bpy.data.objects[self.armature]
                        
            for bone in getHiddenBones():
            
                if armature.pose.bones[bone.name].bone_group.name == self.itemName:
                
                    bone.hide = False
                    bone.select = True
        
        return {'FINISHED'}



class UnHideAllByTypeMenu(bpy.types.Menu):
    bl_label = "Unhide all by type"
    bl_idname = "view3d.unhide_all_by_type_menu"

    def draw(self, context):
        layout = self.layout

        objectTypes = []
            
        for object in getHiddenObjects():
                            
            if object.type not in objectTypes:
                
                row = layout.row()
                operator = row.operator("object.show", text=object.type.lower().capitalize(), icon="OUTLINER_OB_"+object.type)
                operator.itemName = object.type
                operator.unHideAll = True 
                
                objectTypes.append(object.type)
        
        

class UnHideByTypeMenu(bpy.types.Menu):
    bl_label = "Unhide by type"
    bl_idname = "view3d.unhide_by_type_menu"

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        
        col = split.column()
        
        if bpy.context.mode == "OBJECT":
        
            for hiddenObject in getHiddenObjects():
            
                if hiddenObject.type == context.object.type:
                    row = col.row()                        
                    operator = row.operator("object.show", text=hiddenObject.name)
                    operator.itemName = hiddenObject.name
                    operator.type = "Object"
                    
        elif bpy.context.mode == "EDIT_ARMATURE":
                
            for hiddenBone in getHiddenBones():
                
                row = col.row()
                operator = row.operator("object.show", text=hiddenBone.name)
                operator.itemName = hiddenBone.name
                operator.type = "Bone"
                operator.armature = bpy.context.active_object.name   
        


class UnHideMenu(bpy.types.Menu):
    bl_label = "Unhide"
    bl_idname = "view3d.unhide_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        split = layout.split()
                        
        col = split.column()
        
        if bpy.context.mode == "OBJECT":
                                
            hiddenObjects = getHiddenObjects()
            hiddenGroups = getHiddenGroups()     
            
        elif bpy.context.mode == "EDIT_ARMATURE":
            
            hiddenObjects = getHiddenBones()
            hiddenGroups = getHiddenBoneGroups()
            
        
        row = col.row()
        if len(hiddenObjects) > 0:

            if bpy.context.mode == "OBJECT":
                
                row.operator("object.hide_view_clear", text="Unhide all objects", icon="RESTRICT_VIEW_OFF")
                row = col.row()
                row.menu(UnHideAllByTypeMenu.bl_idname, text="UnHide all by type", icon="FILTER")
                row = col.row()
                operator = row.operator("object.unhide_search", text="Search", icon="VIEWZOOM")
            
            elif bpy.context.mode == "EDIT_ARMATURE":
                
                row.operator("armature.reveal", text="Unhide all bones", icon="RESTRICT_VIEW_OFF")
                row = col.row()
                operator = row.operator("object.unhide_search", text="Search", icon="VIEWZOOM")    
                        
        else:
            
            if bpy.context.mode == "OBJECT":
            
                row.label(text="No hidden objects or groups")
            
            elif bpy.context.mode == "EDIT_ARMATURE":
                
                row.label(text="No hidden bones or bone groups")
                
                
        if len(hiddenGroups) > 0:
            col.separator()            
            row = col.row()
            row.label(text="Hidden groups:")
            

        for hiddenGroup in hiddenGroups:
                
            row = col.row()
            operator = row.operator("object.show", text=hiddenGroup.name, icon="GROUP")
            operator.itemName = hiddenGroup.name
            
            if bpy.context.mode == "OBJECT":
                    
                operator.type = "Group"
                
            elif bpy.context.mode == "EDIT_ARMATURE":
            
                operator.type = "Bone Group"
                operator.armature = bpy.context.active_object.name

      
        col.separator()
        
        if len(hiddenObjects) > 0:
            row = col.row()
            row.label(text="Hidden objects by type:")
        
        if bpy.context.mode == "OBJECT":

            objectTypes = []
            
            for object in hiddenObjects:
                                
                if object.type not in objectTypes:
                                    
                    row = layout.row()
                    row.context_pointer_set("object", object)    
                    row.menu(UnHideByTypeMenu.bl_idname, text=object.type.lower().capitalize(), icon="OUTLINER_OB_"+object.type)      

                    objectTypes.append(object.type)
                    
        elif bpy.context.mode == "EDIT_ARMATURE":
                
            row = layout.row()
            row.menu(UnHideByTypeMenu.bl_idname, text="Bone", icon="BONE_DATA")
                
            

keymaps = []
                  
def register():
        
    bpy.utils.register_module(__name__)    
                
    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'H', 'PRESS', alt=True)
    kmi.properties.name = 'view3d.unhide_menu'
    keymaps.append((km, kmi))
    
    km = wm.keyconfigs.addon.keymaps.new(name='Armature', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'H', 'PRESS', alt=True)
    kmi.properties.name = 'view3d.unhide_menu'
    keymaps.append((km, kmi))
        


def unregister():
    bpy.utils.unregister_module(__name__)        
        
    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()
    


if __name__ == "__main__":
    register()

             