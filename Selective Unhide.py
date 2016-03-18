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
    """Unhide the object chosen in the Unhide menu"""
    bl_idname = "object.show"
    bl_label = "Show a specific object"
    bl_options = {"INTERNAL"}

    objectName = bpy.props.StringProperty()

    def execute(self, context):
        
        bpy.data.objects[self.objectName].hide = False
        bpy.data.objects[self.objectName].select = True
        bpy.context.scene.objects.active = bpy.data.objects[self.objectName]
        
        return {'FINISHED'}



class UnHideMenu(bpy.types.Menu):
    bl_label = "Unhide"
    bl_idname = "view3d.unhide_menu"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("object.hide_view_clear", text="Unhide all objects", icon="RESTRICT_VIEW_OFF")
        
        row = layout.row()
        row.label(text="Hidden objects:")
        
        hiddenObjects = (object for object in bpy.context.scene.objects if object.hide)
        
        for hiddenObject in hiddenObjects:
                        
            row = layout.row()
            row.operator("object.show", text=hiddenObject.name, icon="OUTLINER_OB_"+hiddenObject.type).objectName = hiddenObject.name
            


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

             