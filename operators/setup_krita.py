import bpy
import os
import tempfile
import subprocess

from ..core.ora_manager import create_transparent_png, create_solid_png, create_ora_file
from ..core.sync_timer import start_sync_timer

class OBJECT_OT_setup_krita_texture(bpy.types.Operator):
    bl_idname = "object.setup_krita_texture"
    bl_label = "Iniciar Proyecto en Krita"
    bl_description = "Genera la textura con el mapa UV integrado y abre Krita automáticamente"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        scene = context.scene
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Selecciona un objeto MESH activo")
            return {'CANCELLED'}

        # Comprobar si el objeto tiene UV Maps
        if not obj.data.uv_layers:
            self.report({'ERROR'}, "El objeto no tiene UV Maps. Desenvuelve las UVs primero (U > Unwrap)")
            return {'CANCELLED'}

        resolution = int(scene.krita_canvas_size)
        krita_path = scene.krita_executable_path

        # 1. Definir directorio temporal garantizado
        temp_dir = os.path.join(tempfile.gettempdir(), "krita_sync_textures")
        os.makedirs(temp_dir, exist_ok=True)

        uv_path = os.path.join(temp_dir, f"{obj.name}_UV_Guide.png")
        paint_path = os.path.join(temp_dir, f"{obj.name}_Paint.png")
        bg_path = os.path.join(temp_dir, f"{obj.name}_Background.png")
        ora_path = os.path.join(temp_dir, f"{obj.name}_BaseColor.ora")
        texture_path = os.path.join(temp_dir, f"{obj.name}_BaseColor.png")

        # Limpiar posibles archivos previos bloqueados
        for p in (uv_path, paint_path, bg_path, ora_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

        # 2. Exportar el Mapa de UVs seleccionando toda la geometría
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.export_layout(
                filepath=uv_path,
                size=(resolution, resolution),
                opacity=0.4,
                modified=True
            )
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception as e:
            if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'ERROR'}, f"No se pudo exportar el UV Layout: {str(e)}")
            return {'CANCELLED'}

        # 3. Crear capas:
        #    - Capa de pintura: transparente
        #    - Capa de fondo: blanco sólido (para evitar que el modelo se vuelva negro)
        #    - Textura base de Blender: blanca sólida inicial
        create_transparent_png(paint_path, resolution, resolution)
        create_solid_png(bg_path, resolution, resolution, 255, 255, 255, 255)
        create_solid_png(texture_path, resolution, resolution, 255, 255, 255, 255)

        # 4. Crear archivo ORA con 3 capas:
        #    - Superior: "Pintura" (vacía, donde pintas)
        #    - Intermedia: "UV Guide" (guía de referencia)
        #    - Inferior: "Fondo" (blanco sólido)
        create_ora_file(ora_path, paint_path, uv_path, bg_path, resolution, resolution)

        # 5. Cargar textura en memoria de Blender
        img = bpy.data.images.load(texture_path, check_existing=False)
        img.name = f"{obj.name}_BaseColor"

        # 6. Asignar la Imagen al Material del Objeto
        if not obj.data.materials:
            mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
            obj.data.materials.append(mat)
        else:
            mat = obj.data.materials[0]

        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Buscar Principled BSDF
        bsdf = nodes.get("Principled BSDF")
        
        # Reutilizar nodo de textura si ya existe uno, o crear nuevo
        tex_node = None
        for n in nodes:
            if n.type == 'TEX_IMAGE':
                tex_node = n
                break

        if not tex_node:
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.location = (-300, 300)

        tex_node.image = img

        if bsdf:
            links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])

        # 7. Cambiar la vista 3D a Material Preview automáticamente para que se vea la textura
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

        # 8. Activar el Auto-Reload de Texturas
        start_sync_timer()

        # 9. Lanzar Krita con el archivo multicapa (.ora)
        if os.path.exists(krita_path):
            try:
                subprocess.Popen([krita_path, ora_path])
                self.report({'INFO'}, "Proyecto Krita iniciado. Modo Material Preview activado.")
            except Exception as e:
                self.report({'ERROR'}, f"Error al lanzar Krita: {str(e)}")
        else:
            self.report({'WARNING'}, "Archivo creado, pero la ruta de Krita no es válida.")

        return {'FINISHED'}
