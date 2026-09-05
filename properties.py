import bpy

def register_properties():
    bpy.types.Scene.krita_canvas_size = bpy.props.EnumProperty(
        name="Tamaño del Lienzo",
        description="Resolución de la textura en píxeles",
        items=[
            ('1024', "1024 x 1024 (1K)", "Textura 1K"),
            ('2048', "2048 x 2048 (2K)", "Textura 2K"),
            ('4096', "4096 x 4096 (4K)", "Textura 4K"),
        ],
        default='2048'
    )

    bpy.types.Scene.krita_executable_path = bpy.props.StringProperty(
        name="Ejecutable de Krita",
        description="Ruta donde está instalado Krita en tu sistema",
        subtype='FILE_PATH',
        default=r"C:\Program Files\Krita (x64)\bin\krita.exe"
    )

def unregister_properties():
    if hasattr(bpy.types.Scene, "krita_canvas_size"):
        del bpy.types.Scene.krita_canvas_size
    if hasattr(bpy.types.Scene, "krita_executable_path"):
        del bpy.types.Scene.krita_executable_path
