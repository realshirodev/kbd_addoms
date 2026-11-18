import bpy
import os
import subprocess
import sys

from ..core.paths import get_file_paths, get_project_directory, find_krita_executable
from ..core.ora_manager import update_ora_uv_guide
from ..core.sync_timer import start_sync_timer, stop_sync_timer

class OBJECT_OT_krita_update_uv_guide(bpy.types.Operator):
    bl_idname = "object.krita_update_uv_guide"
    bl_label = "Actualizar Guía UV en Krita"
    bl_description = "Exporta de nuevo el mapa de UVs y actualiza la capa UV Guide en el archivo .ora existente sin tocar tu pintura"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        scene = context.scene

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Selecciona un objeto MESH activo")
            return {'CANCELLED'}

        if not obj.data.uv_layers:
            self.report({'ERROR'}, "El objeto no tiene UV Maps")
            return {'CANCELLED'}

        paths = get_file_paths(context, obj.name, scene.krita_texture_channel)
        ora_path = paths["ora_path"]
        uv_path = paths["uv_path"]
        resolution = int(scene.krita_canvas_size)

        if not os.path.exists(ora_path):
            self.report({'WARNING'}, "No existe un archivo .ora previo para este objeto. Usa 'Iniciar Proyecto en Krita' primero.")
            return {'CANCELLED'}

        # Exportar UVs de forma segura
        prev_mode = obj.mode
        try:
            context.view_layer.objects.active = obj
            obj.select_set(True)
            if prev_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            
            bpy.ops.uv.export_layout(
                filepath=uv_path,
                mode='PNG',
                size=(resolution, resolution),
                opacity=scene.krita_uv_opacity,
                modified=True,
                export_all=True,
                check_existing=False
            )
        except Exception as e:
            self.report({'ERROR'}, f"Error al exportar UV: {str(e)}")
            return {'CANCELLED'}
        finally:
            if bpy.context.object and bpy.context.object.mode != prev_mode:
                try:
                    bpy.ops.object.mode_set(mode=prev_mode)
                except Exception:
                    pass

        # Inyectar el nuevo mapa UV dentro del archivo ORA
        try:
            success = update_ora_uv_guide(ora_path, uv_path)
            if success:
                self.report({'INFO'}, "Guía UV actualizada en el proyecto Krita sin alterar tus capas de pintura")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "No se pudo actualizar la capa UV en el archivo .ora")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Fallo al actualizar .ora: {str(e)}")
            return {'CANCELLED'}


class OBJECT_OT_krita_pack_texture(bpy.types.Operator):
    bl_idname = "object.krita_pack_texture"
    bl_label = "Empaquetar Textura en .blend"
    bl_description = "Incrusta los datos de la textura directamente dentro del archivo .blend para no perderla nunca"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        scene = context.scene

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Selecciona un objeto MESH activo")
            return {'CANCELLED'}

        paths = get_file_paths(context, obj.name, scene.krita_texture_channel)
        tex_path = paths["texture_path"]

        found_img = None
        for img in bpy.data.images:
            if img.filepath and os.path.normpath(bpy.path.abspath(img.filepath)) == tex_path:
                found_img = img
                break

        if not found_img:
            # Buscar por nombre del canal
            found_img = bpy.data.images.get(paths["base_name"])

        if not found_img:
            self.report({'WARNING'}, "No se encontró la imagen en memoria para empaquetar")
            return {'CANCELLED'}

        try:
            found_img.pack()
            self.report({'INFO'}, f"Textura '{found_img.name}' empaquetada permanentemente en el archivo .blend")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"No se pudo empaquetar la imagen: {str(e)}")
            return {'CANCELLED'}


class OBJECT_OT_krita_save_texture(bpy.types.Operator):
    bl_idname = "object.krita_save_texture"
    bl_label = "Guardar Textura a Disco"
    bl_description = "Fuerza el guardado del bloque de imagen actual directamente en el archivo PNG del disco"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        scene = context.scene

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Selecciona un objeto MESH activo")
            return {'CANCELLED'}

        paths = get_file_paths(context, obj.name, scene.krita_texture_channel)
        tex_path = paths["texture_path"]

        found_img = None
        for img in bpy.data.images:
            if img.filepath and os.path.normpath(bpy.path.abspath(img.filepath)) == tex_path:
                found_img = img
                break

        if not found_img:
            found_img = bpy.data.images.get(paths["base_name"])

        if not found_img:
            self.report({'WARNING'}, "No se encontró la imagen en memoria")
            return {'CANCELLED'}

        try:
            found_img.save()
            self.report({'INFO'}, f"Textura guardada con éxito en: {tex_path}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error al guardar imagen: {str(e)}")
            return {'CANCELLED'}


class OBJECT_OT_krita_open_folder(bpy.types.Operator):
    bl_idname = "object.krita_open_folder"
    bl_label = "Abrir Carpeta de Texturas"
    bl_description = "Abre en el Explorador de Archivos la carpeta donde se guardan las texturas y proyectos"
    bl_options = {'REGISTER'}

    def execute(self, context):
        dir_path, status = get_project_directory(context)
        if not dir_path or not os.path.exists(dir_path):
            self.report({'WARNING'}, "La carpeta de texturas aún no ha sido creada o no existe en disco")
            return {'CANCELLED'}

        try:
            if sys.platform.startswith("win"):
                os.startfile(dir_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", dir_path])
            else:
                subprocess.Popen(["xdg-open", dir_path])
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"No se pudo abrir el explorador: {str(e)}")
            return {'CANCELLED'}


class OBJECT_OT_krita_toggle_sync(bpy.types.Operator):
    bl_idname = "object.krita_toggle_sync"
    bl_label = "Pausar / Reanudar Sincronización"
    bl_description = "Alterna el estado de recarga automática en tiempo real desde Krita"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        new_state = not scene.krita_sync_active
        scene.krita_sync_active = new_state

        if new_state:
            start_sync_timer()
            self.report({'INFO'}, "Sincronización en vivo ACTIVADA")
        else:
            self.report({'INFO'}, "Sincronización en vivo PAUSADA")

        return {'FINISHED'}


class OBJECT_OT_krita_detect_path(bpy.types.Operator):
    bl_idname = "object.krita_detect_path"
    bl_label = "Detectar Krita Automáticamente"
    bl_description = "Busca la instalación de Krita en el sistema y la asigna a la configuración"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        detected = find_krita_executable()
        if detected and os.path.exists(detected):
            context.scene.krita_executable_path = detected
            self.report({'INFO'}, f"Krita detectado en: {detected}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No se encontró Krita en las rutas habituales. Por favor selecciona el ejecutable manualmente.")
            return {'CANCELLED'}

