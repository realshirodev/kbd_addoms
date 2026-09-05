bl_info = {
    "name": "Krita Live Texturing",
    "author": "ShiroDev",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Krita Sync",
    "description": "Automatiza la exportacion de UVs, creacion de lienzo y sincronizacion con Krita",
    "category": "Material",
    "youtube channel": "https://www.youtube.com/@shiro_dev"
}

import bpy
from .core.security import verify_author_integrity
from .core.sync_timer import stop_sync_timer
from .properties import register_properties, unregister_properties
from .operators.setup_krita import OBJECT_OT_setup_krita_texture
from .ui.panel import VIEW3D_PT_krita_sync_panel

classes = (
    OBJECT_OT_setup_krita_texture,
    VIEW3D_PT_krita_sync_panel,
)

def register():
    # Validación de integridad de autoría
    if not verify_author_integrity(bl_info):
        raise RuntimeError(
            "\n[SEGURIDAD] Error de integridad: Este complemento ha sido modificado o la autoría "
            "original de 'ShiroDev' ha sido alterada. El addon no puede iniciarse."
        )

    register_properties()

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    stop_sync_timer()
    unregister_properties()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
