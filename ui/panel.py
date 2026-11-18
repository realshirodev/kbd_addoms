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
        obj = context.active_object

        # 1. Estado y Objeto Activo
        header_box = layout.box()
        h_row = header_box.row(align=True)
        if obj and obj.type == 'MESH':
            h_row.label(text=f"Malla: {obj.name}", icon='MESH_DATA')
        else:
            h_row.label(text="Sin malla activa", icon='ERROR')

        # Indicador de estado de sincronización
        sync_active = getattr(scene, "krita_sync_active", True)
        sync_row = header_box.row(align=True)
        if sync_active:
            sync_row.label(text="🟢 Sincronización Activa", icon='FILE_REFRESH')
            sync_row.operator("object.krita_toggle_sync", text="Pausar", icon='PAUSE')
        else:
            sync_row.label(text="⏸️ Sincronización Pausada", icon='PAUSE')
            sync_row.operator("object.krita_toggle_sync", text="Reanudar", icon='PLAY')

        # 2. Guardado y Persistencia (No perder imágenes)
        save_box = layout.box()
        save_box.label(text="Almacenamiento & Guardado", icon='FILE_FOLDER')
        save_col = save_box.column(align=True)
        save_col.prop(scene, "krita_storage_mode", text="Guardar en")

        mode = scene.krita_storage_mode
        if mode == 'BLEND_DIR':
            save_col.prop(scene, "krita_subfolder", text="Subcarpeta")
            if not (bpy.data.is_saved and bpy.data.filepath):
                warn_box = save_box.box()
                warn_box.alert = True
                warn_box.label(text="⚠️ Archivo .blend no guardado", icon='ERROR')
                warn_box.label(text="Guarda tu proyecto con Ctrl+S para")
                warn_box.label(text="almacenar las texturas en su carpeta.")
        elif mode == 'CUSTOM':
            save_col.prop(scene, "krita_custom_dir", text="Carpeta")
            if not scene.krita_custom_dir.strip():
                warn_box = save_box.box()
                warn_box.alert = True
                warn_box.label(text="⚠️ Elige una carpeta de destino", icon='ERROR')
        else:  # 'TEMP'
            note_row = save_box.row()
            note_row.alert = True
            note_row.label(text="⚠️ Temporal: se borrará al reiniciar PC", icon='INFO')

        save_box.prop(scene, "krita_auto_pack", text="Auto-empaquetar en .blend")

        # 3. Configuración de Lienzo y PBR
        canvas_box = layout.box()
        canvas_box.label(text="Configuración de Lienzo", icon='TEXTURE')
        canvas_col = canvas_box.column(align=True)
        canvas_col.prop(scene, "krita_texture_channel", text="Canal PBR")
        canvas_col.prop(scene, "krita_canvas_size", text="Resolución")
        canvas_col.prop(scene, "krita_bg_color", text="Fondo")

        uv_row = canvas_box.row(align=True)
        uv_row.prop(scene, "krita_uv_opacity", text="Opacidad UV", slider=True)
        uv_row.prop(scene, "krita_uv_visible", text="", icon='HIDE_OFF' if scene.krita_uv_visible else 'HIDE_ON')

        layout.separator()

        # 4. Botón Principal
        main_col = layout.column(align=True)
        main_row = main_col.row()
        main_row.scale_y = 1.6
        main_row.operator("object.setup_krita_texture", icon='BRUSH_DATA', text="Iniciar / Abrir en Krita")
        main_col.prop(scene, "krita_overwrite_project", text="Sobrescribir archivo si ya existe")

        layout.separator()

        # 5. Herramientas de Textura
        tools_box = layout.box()
        tools_box.label(text="Herramientas de Textura", icon='TOOL_SETTINGS')
        
        t_row1 = tools_box.row(align=True)
        t_row1.operator("object.krita_update_uv_guide", icon='UV_DATA', text="Actualizar UV")
        t_row1.operator("object.krita_open_folder", icon='FILE_FOLDER', text="Abrir Carpeta")

        t_row2 = tools_box.row(align=True)
        t_row2.operator("object.krita_pack_texture", icon='PACKAGE', text="Empaquetar .blend")
        t_row2.operator("object.krita_save_texture", icon='FILE_TICK', text="Guardar a Disco")

        # 6. Configuración de Krita
        krita_box = layout.box()
        krita_box.label(text="Configuración de Krita", icon='PREFERENCES')
        k_col = krita_box.column(align=True)
        k_col.prop(scene, "krita_executable_path", text="Ruta")
        
        k_actions = krita_box.row(align=True)
        k_actions.operator("object.krita_detect_path", text="Auto-detectar Krita", icon='VIEWZOOM')
        k_actions.prop(scene, "krita_sync_interval", text="Intervalo (s)")

        layout.separator()

        # 7. Sección de autoría y canal oficial (Intacta)
        box = layout.box()
        b_row = box.row(align=True)
        b_row.label(text="Dev: ShiroDev", icon='USER')
        
        url_op = box.operator("wm.url_open", text="YouTube Channel", icon='URL')
        url_op.url = "https://www.youtube.com/@shiro_dev"
        
        site_op = box.operator("wm.url_open", text="Team Apricot", icon='GLOBE')
        site_op.url = "https://teamapricot.com"
