import bpy
from .core.paths import find_krita_executable

def register_properties():
    # 1. Almacenamiento y persistencia
    bpy.types.Scene.krita_storage_mode = bpy.props.EnumProperty(
        name="Modo de Almacenamiento",
        description="Dónde se guardarán los archivos del proyecto .ora y las texturas de imagen",
        items=[
            ('BLEND_DIR', "Junto al archivo .blend", "Guarda en una subcarpeta junto al archivo .blend actual (Recomendado)"),
            ('CUSTOM', "Carpeta personalizada", "Permite elegir una carpeta específica en el disco"),
            ('TEMP', "Directorio temporal", "Guarda en la carpeta temporal del sistema (los archivos pueden eliminarse al reiniciar)"),
        ],
        default='BLEND_DIR'
    )

    bpy.types.Scene.krita_subfolder = bpy.props.StringProperty(
        name="Subcarpeta",
        description="Nombre de la subcarpeta junto al archivo .blend donde se guardarán las texturas",
        default="textures"
    )

    bpy.types.Scene.krita_custom_dir = bpy.props.StringProperty(
        name="Carpeta Destino",
        description="Directorio personalizado donde guardar las texturas y el archivo de Krita",
        subtype='DIR_PATH',
        default=""
    )

    bpy.types.Scene.krita_auto_pack = bpy.props.BoolProperty(
        name="Empaquetar en .blend",
        description="Empaqueta automáticamente la textura dentro del archivo .blend para no perderla nunca al mover o compartir el archivo",
        default=True
    )

    # 2. Configuración de lienzo y resolución
    bpy.types.Scene.krita_canvas_size = bpy.props.EnumProperty(
        name="Tamaño del Lienzo",
        description="Resolución de la textura en píxeles",
        items=[
            ('512', "512 x 512 (Retro / Baja)", "Textura 512px"),
            ('1024', "1024 x 1024 (1K)", "Textura 1K estándar"),
            ('2048', "2048 x 2048 (2K)", "Textura 2K alta resolución"),
            ('4096', "4096 x 4096 (4K)", "Textura 4K ultra resolución"),
            ('8192', "8192 x 8192 (8K)", "Textura 8K máxima fidelidad"),
        ],
        default='2048'
    )

    # 3. Canales PBR
    bpy.types.Scene.krita_texture_channel = bpy.props.EnumProperty(
        name="Canal / Ranura",
        description="Canal de textura a pintar y conectar en el shader Principled BSDF",
        items=[
            ('BaseColor', "Color Base (Albedo)", "Color difuso del material"),
            ('Roughness', "Rugosidad (Roughness)", "Aspereza o brillo de la superficie (Espacio Non-Color)"),
            ('Metallic', "Metálico (Metallic)", "Nivel metálico del material (Espacio Non-Color)"),
            ('Normal', "Mapa de Normales (Normal)", "Detalles de relieve con normales tangentes"),
            ('Emission', "Emisión (Emission)", "Luz propia emitida por la superficie"),
        ],
        default='BaseColor'
    )

    # 4. Color de fondo del lienzo
    bpy.types.Scene.krita_bg_color = bpy.props.EnumProperty(
        name="Color de Fondo",
        description="Color inicial para la capa de fondo",
        items=[
            ('WHITE', "Blanco (White)", "Fondo blanco sólido"),
            ('GRAY', "Gris Neutro (Gray)", "Fondo gris al 50%"),
            ('BLACK', "Negro (Black)", "Fondo negro sólido"),
            ('TRANSPARENT', "Transparente", "Fondo sin color (alfa cero)"),
        ],
        default='WHITE'
    )

    # 5. Guía UV
    bpy.types.Scene.krita_uv_opacity = bpy.props.FloatProperty(
        name="Opacidad Guía UV",
        description="Opacidad con la que se inserta el mapa UV en Krita",
        default=0.35,
        min=0.05,
        max=1.0,
        subtype='FACTOR'
    )

    bpy.types.Scene.krita_uv_visible = bpy.props.BoolProperty(
        name="Guía UV Visible",
        description="Determina si la capa de guía UV está visible por defecto al abrir Krita",
        default=True
    )

    # 6. Ejecutable de Krita
    default_krita = find_krita_executable() or r"C:\Program Files\Krita (x64)\bin\krita.exe"
    bpy.types.Scene.krita_executable_path = bpy.props.StringProperty(
        name="Ejecutable de Krita",
        description="Ruta donde está instalado Krita en tu sistema",
        subtype='FILE_PATH',
        default=default_krita
    )

    # 7. Control de proyectos y sincronización
    bpy.types.Scene.krita_overwrite_project = bpy.props.BoolProperty(
        name="Sobrescribir si existe",
        description="Si está desactivado y el archivo .ora ya existe, se abre en Krita sin borrar las capas previas de pintura",
        default=False
    )

    bpy.types.Scene.krita_sync_active = bpy.props.BoolProperty(
        name="Sincronización en Vivo",
        description="Activa o pausa la sincronización automática de texturas en tiempo real",
        default=True
    )

    bpy.types.Scene.krita_sync_interval = bpy.props.FloatProperty(
        name="Intervalo de Refresco",
        description="Intervalo en segundos para comprobar cambios en disco (0.1 a 3.0)",
        default=0.3,
        min=0.1,
        max=3.0
    )


def unregister_properties():
    props = [
        "krita_storage_mode",
        "krita_subfolder",
        "krita_custom_dir",
        "krita_auto_pack",
        "krita_canvas_size",
        "krita_texture_channel",
        "krita_bg_color",
        "krita_uv_opacity",
        "krita_uv_visible",
        "krita_executable_path",
        "krita_overwrite_project",
        "krita_sync_active",
        "krita_sync_interval",
    ]
    for prop in props:
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)
