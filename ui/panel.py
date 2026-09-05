import bpy

class VIEW3D_PT_krita_sync_panel(bpy.types.Panel):
    bl_label = "Krita Live Sync"
    bl_idname = "VIEW3D_PT_krita_sync_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Krita Sync'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Opciones de lienzo y ejecutable
        col = layout.column(align=True)
        col.prop(scene, "krita_canvas_size", text="Lienzo")
        col.prop(scene, "krita_executable_path", text="Ruta Krita")
        
        layout.separator()
        
        # Botón principal
        row = layout.row()
        row.scale_y = 1.3
        row.operator("object.setup_krita_texture", icon='TEXTURE', text="Iniciar Proyecto en Krita")

        layout.separator()

        # Sección de autoría y canal oficial
        box = layout.box()
        b_row = box.row(align=True)
        b_row.label(text="Dev: ShiroDev", icon='USER')
        
        url_op = box.operator("wm.url_open", text="YouTube Channel", icon='URL')
        url_op.url = "https://www.youtube.com/@shiro_dev"
