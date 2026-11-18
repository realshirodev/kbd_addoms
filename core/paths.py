import os
import sys
import shutil
import tempfile
import bpy

def find_krita_executable() -> str:
    """Busca automáticamente el ejecutable de Krita en las rutas más comunes y en el PATH."""
    # 1. Comprobar PATH
    which_krita = shutil.which("krita") or shutil.which("krita.exe")
    if which_krita and os.path.isfile(which_krita):
        return os.path.normpath(which_krita)

    # 2. Rutas comunes en Windows
    if sys.platform.startswith("win"):
        candidates = [
            r"C:\Program Files\Krita (x64)\bin\krita.exe",
            r"C:\Program Files\Krita\bin\krita.exe",
            r"C:\Program Files (x86)\Krita\bin\krita.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Krita (x64)\bin\krita.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Krita\bin\krita.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Krita (x64)\bin\krita.exe"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return os.path.normpath(c)

    # 3. macOS
    elif sys.platform == "darwin":
        mac_candidates = [
            "/Applications/Krita.app/Contents/MacOS/krita",
            os.path.expanduser("~/Applications/Krita.app/Contents/MacOS/krita"),
        ]
        for c in mac_candidates:
            if os.path.isfile(c):
                return c

    # 4. Linux / Unix
    else:
        linux_candidates = [
            "/usr/bin/krita",
            "/usr/local/bin/krita",
            "/var/lib/flatpak/exports/bin/org.kde.krita",
            os.path.expanduser("~/.local/share/flatpak/exports/bin/org.kde.krita"),
            "/snap/bin/krita",
        ]
        for c in linux_candidates:
            if os.path.isfile(c):
                return c

    return ""


def get_project_directory(context) -> tuple[str | None, str]:
    """Obtiene el directorio de destino según la configuración seleccionada en Scene.
    
    Retorna una tupla: (ruta_o_None, estado_string)
    Estados posibles: 'blend_ok', 'blend_unsaved', 'custom_ok', 'custom_empty', 'temp_ok'
    """
    scene = context.scene
    mode = getattr(scene, "krita_storage_mode", "BLEND_DIR")

    if mode == "BLEND_DIR":
        if bpy.data.is_saved and bpy.data.filepath:
            blend_dir = os.path.dirname(bpy.path.abspath(bpy.data.filepath))
            subfolder = getattr(scene, "krita_subfolder", "textures").strip()
            target = os.path.join(blend_dir, subfolder) if subfolder else blend_dir
            return os.path.normpath(target), "blend_ok"
        else:
            return None, "blend_unsaved"

    elif mode == "CUSTOM":
        custom_dir = getattr(scene, "krita_custom_dir", "").strip()
        if custom_dir:
            abs_dir = bpy.path.abspath(custom_dir)
            return os.path.normpath(abs_dir), "custom_ok"
        else:
            return None, "custom_empty"

    else:  # 'TEMP'
        temp_dir = os.path.join(tempfile.gettempdir(), "krita_sync_textures")
        return os.path.normpath(temp_dir), "temp_ok"


def get_file_paths(context, obj_name: str, channel_name: str = "BaseColor") -> dict:
    """Calcula todas las rutas de archivo necesarias para un objeto y canal específicos."""
    dir_path, status = get_project_directory(context)
    
    # Si la ruta no está disponible directamente (ej: blend sin guardar), usar temporal como respaldo seguro
    if not dir_path:
        dir_path = os.path.normpath(os.path.join(tempfile.gettempdir(), "krita_sync_textures"))

    # Sanear nombres de archivo
    safe_obj = "".join(c for c in obj_name if c.isalnum() or c in ('_', '-'))
    safe_channel = "".join(c for c in channel_name if c.isalnum() or c in ('_', '-'))
    base_name = f"{safe_obj}_{safe_channel}"

    return {
        "dir": dir_path,
        "status": status,
        "base_name": base_name,
        "uv_path": os.path.normpath(os.path.join(dir_path, f"{safe_obj}_UV_Guide.png")),
        "paint_path": os.path.normpath(os.path.join(dir_path, f"{base_name}_Paint.png")),
        "bg_path": os.path.normpath(os.path.join(dir_path, f"{base_name}_Background.png")),
        "ora_path": os.path.normpath(os.path.join(dir_path, f"{base_name}.ora")),
        "texture_path": os.path.normpath(os.path.join(dir_path, f"{base_name}.png")),
    }

