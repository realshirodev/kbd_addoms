from .setup_krita import OBJECT_OT_setup_krita_texture
from .extra_ops import (
    OBJECT_OT_krita_update_uv_guide,
    OBJECT_OT_krita_pack_texture,
    OBJECT_OT_krita_save_texture,
    OBJECT_OT_krita_open_folder,
    OBJECT_OT_krita_toggle_sync,
    OBJECT_OT_krita_detect_path,
)

operator_classes = (
    OBJECT_OT_setup_krita_texture,
    OBJECT_OT_krita_update_uv_guide,
    OBJECT_OT_krita_pack_texture,
    OBJECT_OT_krita_save_texture,
    OBJECT_OT_krita_open_folder,
    OBJECT_OT_krita_toggle_sync,
    OBJECT_OT_krita_detect_path,
)
