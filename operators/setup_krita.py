import bpy
import os
import subprocess

from ..core.ora_manager import (
    create_transparent_png,
    create_solid_png,
    create_ora_file,
    extract_composite_from_ora
)
from ..core.paths import get_file_paths, find_krita_executable
from ..core.sync_timer import start_sync_timer

class OBJECT_OT_setup_krita_texture(bpy.types.Operator):
    bl_idname = "object.setup_krita_texture"
    bl_label = "Iniciar Proyecto en Krita"
    bl_description = "Genera el proyecto multicapa o abre el existente en Krita con sincronización en tiempo real"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        scene = context.scene

        # 1. Validación de objeto
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Selecciona un objeto MESH activo")
            return {'CANCELLED'}

        # Comprobar si el objeto tiene UV Maps
        if not obj.data.uv_layers:
            self.report({'ERROR'}, "El objeto no tiene UV Maps. Desenvuelve las UVs primero (Modo Edición > U > Unwrap)")
            return {'CANCELLED'}

        resolution = int(scene.krita_canvas_size)
        channel = scene.krita_texture_channel

        # 2. Resolución de rutas seguras y persistentes
        paths = get_file_paths(context, obj.name, channel)
        status = paths["status"]

        if status == "blend_unsaved":
            self.report(
                {'ERROR'},
                "El archivo .blend aún no ha sido guardado. Guarda tu proyecto (Ctrl+S) para guardar las texturas junto a él, "
                "o cambia el 'Modo de Almacenamiento' a 'Carpeta personalizada'."
            )
            return {'CANCELLED'}
        elif status == "custom_empty":
            self.report(
                {'ERROR'},
                "Has seleccionado 'Carpeta personalizada' pero no has indicado una ruta. Elige una carpeta en el panel."
            )
            return {'CANCELLED'}

        target_dir = paths["dir"]
        os.makedirs(target_dir, exist_ok=True)

        uv_path = paths["uv_path"]
        paint_path = paths["paint_path"]
        bg_path = paths["bg_path"]
        ora_path = paths["ora_path"]
        texture_path = paths["texture_path"]
        base_name = paths["base_name"]

        project_exists = os.path.exists(ora_path)
        overwrite = scene.krita_overwrite_project

        # 3. Creación o reutilización de archivos
        if project_exists and not overwrite:
            # Reutilizar proyecto existente para no destruir las capas de pintura del artista
            if not os.path.exists(texture_path):
                # Extraer composite previo si faltaba el PNG
                extracted = extract_composite_from_ora(ora_path, texture_path)
                if not extracted:
                    create_solid_png(texture_path, resolution, resolution, 255, 255, 255, 255)
            self.report({'INFO'}, f"Proyecto existente detectado. Abriendo en Krita sin sobrescribir pintura.")
        else:
            # Exportar el Mapa de UVs seleccionando toda la geometría de forma segura
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
                self.report({'ERROR'}, f"No se pudo exportar el UV Layout: {str(e)}")
                return {'CANCELLED'}
            finally:
                if bpy.context.object and bpy.context.object.mode != prev_mode:
                    try:
                        bpy.ops.object.mode_set(mode=prev_mode)
                    except Exception:
                        pass

            # Determinar color de fondo
            bg_choice = scene.krita_bg_color
            if bg_choice == 'WHITE':
                r, g, b, a = 255, 255, 255, 255
            elif bg_choice == 'GRAY':
                r, g, b, a = 128, 128, 128, 255
            elif bg_choice == 'BLACK':
                r, g, b, a = 0, 0, 0, 255
            else:  # TRANSPARENT
                r, g, b, a = 0, 0, 0, 0

            # Crear capas iniciales
            create_transparent_png(paint_path, resolution, resolution)
            create_solid_png(bg_path, resolution, resolution, r, g, b, a)
            create_solid_png(texture_path, resolution, resolution, r, g, b, a)

            # Crear archivo multicapa OpenRaster (.ora)
            create_ora_file(
                ora_path,
                paint_path,
                uv_path,
                bg_path,
                resolution,
                resolution,
                uv_opacity=scene.krita_uv_opacity,
                uv_visible=scene.krita_uv_visible
            )

        # 4. Gestión limpia del bloque de imagen en memoria de Blender (evitando duplicados .001, .002)
        img = None
        for existing in bpy.data.images:
            if existing.filepath and os.path.normpath(bpy.path.abspath(existing.filepath)) == texture_path:
                img = existing
                break

        if not img:
            img = bpy.data.images.get(base_name)

        if not img:
            img = bpy.data.images.load(texture_path, check_existing=True)
            img.name = base_name
        else:
            img.filepath = texture_path
            try:
                img.reload()
            except Exception:
                pass

        # Configurar espacio de color según el tipo de canal PBR
        if channel in ('Roughness', 'Metallic', 'Normal'):
            try:
                img.colorspace_settings.name = 'Non-Color'
            except Exception:
                pass
        else:
            try:
                img.colorspace_settings.name = 'sRGB'
            except Exception:
                pass

        # Empaquetado automático si está habilitado
        if scene.krita_auto_pack:
            try:
                img.pack()
            except Exception:
                pass

        # 5. Configurar Material y Nodos de Shader
        if not obj.data.materials:
            mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
            obj.data.materials.append(mat)
        else:
            mat = obj.data.materials[0]
            if not mat:
                mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
                obj.data.materials[0] = mat

        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Buscar o crear Principled BSDF
        bsdf = None
        for n in nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break

        if not bsdf:
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 300)

            # Conectar BSDF a la salida del material
            output_node = None
            for n in nodes:
                if n.type == 'OUTPUT_MATERIAL':
                    output_node = n
                    break
            if not output_node:
                output_node = nodes.new(type='ShaderNodeOutputMaterial')
                output_node.location = (300, 300)

            surf_in = output_node.inputs.get('Surface') or output_node.inputs[0]
            bsdf_out = bsdf.outputs.get('BSDF') or bsdf.outputs[0]
            links.new(bsdf_out, surf_in)

        # Buscar o crear nodo de textura de imagen específico para este canal
        tex_node = None
        for n in nodes:
            if n.type == 'TEX_IMAGE' and n.image == img:
                tex_node = n
                break

        if not tex_node:
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.image = img
            # Posicionamiento dinámico según canal
            pos_offsets = {
                'BaseColor': (-400, 300),
                'Roughness': (-400, 50),
                'Metallic': (-400, -200),
                'Normal': (-600, -450),
                'Emission': (-400, -700),
            }
            tex_node.location = pos_offsets.get(channel, (-400, 300))

        tex_node.label = f"Krita: {channel}"

        # Conectar al socket correspondiente del Principled BSDF
        if channel == 'BaseColor':
            target_socket = bsdf.inputs.get('Base Color')
            if target_socket:
                links.new(tex_node.outputs['Color'], target_socket)

        elif channel == 'Roughness':
            target_socket = bsdf.inputs.get('Roughness')
            if target_socket:
                links.new(tex_node.outputs['Color'], target_socket)

        elif channel == 'Metallic':
            target_socket = bsdf.inputs.get('Metallic')
            if target_socket:
                links.new(tex_node.outputs['Color'], target_socket)

        elif channel == 'Normal':
            # Buscar o crear nodo Normal Map
            norm_node = None
            for n in nodes:
                if n.type == 'NORMAL_MAP':
                    norm_node = n
                    break
            if not norm_node:
                norm_node = nodes.new(type='ShaderNodeNormalMap')
                norm_node.location = (-300, -450)

            links.new(tex_node.outputs['Color'], norm_node.inputs['Color'])
            target_socket = bsdf.inputs.get('Normal')
            if target_socket:
                links.new(norm_node.outputs['Normal'], target_socket)

        elif channel == 'Emission':
            target_socket = bsdf.inputs.get('Emission Color') or bsdf.inputs.get('Emission')
            if target_socket:
                links.new(tex_node.outputs['Color'], target_socket)

        # 6. Cambiar la vista 3D a Material Preview automáticamente
        if context.screen:
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'MATERIAL'

        # 7. Activar el Auto-Reload de Texturas
        start_sync_timer()

        # 8. Lanzar Krita con el archivo multicapa (.ora)
        krita_path = scene.krita_executable_path
        if not krita_path or not os.path.exists(krita_path):
            detected = find_krita_executable()
            if detected:
                scene.krita_executable_path = detected
                krita_path = detected

        if krita_path and os.path.exists(krita_path):
            try:
                subprocess.Popen([krita_path, ora_path])
                self.report({'INFO'}, f"Krita iniciado con éxito. Archivo: {os.path.basename(ora_path)}")
            except Exception as e:
                self.report({'ERROR'}, f"Error al lanzar Krita: {str(e)}")
        else:
            self.report({'WARNING'}, "Archivos guardados en disco, pero no se encontró la ruta de Krita para abrirlo automáticamente.")

        return {'FINISHED'}
