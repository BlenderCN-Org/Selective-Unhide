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



class UnhideObject(bpy.types.Operator):
    """Unhide the object or group of objects"""
    bl_idname = "object.show"
    bl_label = "Show a specific object or group"
    bl_options = {"INTERNAL"}

    itemName = bpy.props.StringProperty()
    type = bpy.props.StringProperty()

    def execute(self, context):
        
        if self.type == "Object":
            
            bpy.data.objects[self.itemName].hide = False
            bpy.data.objects[self.itemName].select = True
            bpy.context.scene.objects.active = bpy.data.objects[self.itemName]
            
        elif self.type == "Group":
            
            for object in bpy.data.groups[self.itemName].objects:
                
                if object.hide:
                
                    object.hide = False
                    object.select = True
        
        return {'FINISHED'}



class UnHideMenu(bpy.types.Menu):
    bl_label = "Unhide"
    bl_idname = "view3d.unhide_menu"

    def draw(self, context):
        layout = self.layout
        
                       
        hiddenObjects = [object for object in bpy.context.scene.objects if object.hide]
        
        row = layout.row()
        if len(hiddenObjects) > 0:
            row.operator("object.hide_view_clear", text="Unhide all objects", icon="RESTRICT_VIEW_OFF")
        else:
            row.label(text="No hidden objects or groups")
        
        #Possible, but not very readable
        #hiddenGroups = [group.name for hiddenObject in hiddenObjects if hiddenObject.name in group.objects and group.name not in hiddenGroups]
        
        hiddenGroups = []
                
        for group in bpy.data.groups:
            
            for hiddenObject in hiddenObjects:

                if hiddenObject.name in group.objects and group.name not in hiddenGroups:
                    
                    hiddenGroups.append(group.name)
                            

        if len(hiddenGroups) > 0:            
            row = layout.row()
            row.label(text="Hidden groups:")
        

        for hiddenGroup in hiddenGroups:
            row = layout.row()
            operator = row.operator("object.show", text=hiddenGroup, icon="GROUP")
            operator.itemName = hiddenGroup
            operator.type = "Group"

        
        if len(hiddenObjects) > 0:
            row = layout.row()
            row.label(text="Hidden objects:")

                
        for hiddenObject in hiddenObjects: 
            row = layout.row()
            operator = row.operator("object.show", text=hiddenObject.name, icon="OUTLINER_OB_"+hiddenObject.type)
            operator.itemName = hiddenObject.name
            operator.type = "Object"


keymaps = []
                  
def register():
    bpy.utils.register_module(__name__)    
            
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    
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

             