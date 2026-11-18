bl_info = {
    "name": "Krita Live Texturing",
    "author": "ShiroDev",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Krita Sync",
    "description": "Automatiza la exportacion de UVs, creacion de lienzo multicapa, soporte PBR y sincronizacion con Krita",
    "category": "Material",
    "doc_url": "https://teamapricot.com/marketplace/krita-live-texturing-for-blender",
    "website": "https://teamapricot.com",
    "youtube_channel": "https://www.youtube.com/@shiro_dev"
}

import sys
import importlib

# Recarga dinámica automática si Blender ya tenía los submódulos en caché
if "bpy" in locals():
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith(__name__ + "."):
            try:
                importlib.reload(sys.modules[mod_name])
            except Exception:
                pass

import bpy
from .core.security import verify_author_integrity
from .core.sync_timer import stop_sync_timer
from .properties import register_properties, unregister_properties
from .operators import operator_classes
from .ui.panel import VIEW3D_PT_krita_sync_panel

classes = operator_classes + (
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
