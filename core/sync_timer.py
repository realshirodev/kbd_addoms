import bpy
import os
import zipfile

last_modified_times = {}

def check_and_reload_textures():
    """Timer periódico de Blender que detecta cuando Krita guarda y recarga en tiempo real."""
    for img in bpy.data.images:
        if img.source == 'FILE' and img.filepath:
            abs_path = bpy.path.abspath(img.filepath)
            
            # Comprobar si existe un archivo .ora asociado a la textura
            base_no_ext = os.path.splitext(abs_path)[0]
            ora_path = base_no_ext + ".ora"
            
            if os.path.exists(ora_path):
                file_to_track = ora_path
                is_ora = True
            elif os.path.exists(abs_path):
                file_to_track = abs_path
                is_ora = False
            else:
                continue

            try:
                mtime = os.path.getmtime(file_to_track)
            except OSError:
                continue

            last_mtime = last_modified_times.get(file_to_track, 0)

            # Inicializar en el primer ciclo
            if file_to_track not in last_modified_times:
                last_modified_times[file_to_track] = mtime
                continue

            # Detectar cambios al guardar (Ctrl+S) en Krita
            if mtime > last_mtime:
                if is_ora:
                    try:
                        with zipfile.ZipFile(ora_path, 'r') as zf:
                            if "mergedimage.png" in zf.namelist():
                                data = zf.read("mergedimage.png")
                                with open(abs_path, 'wb') as f:
                                    f.write(data)
                    except (zipfile.BadZipFile, PermissionError, OSError):
                        # Si Krita aún está escribiendo en disco, esperar al siguiente ciclo (0.3s)
                        continue

                last_modified_times[file_to_track] = mtime
                img.reload()

                # Forzar refresco inmediato del Viewport 3D
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()

                print(f"[Krita-Sync] Textura recargada automáticamente: {img.name}")
    return 0.3

def start_sync_timer():
    """Registra el temporizador si no está activo."""
    if not bpy.app.timers.is_registered(check_and_reload_textures):
        bpy.app.timers.register(check_and_reload_textures)

def stop_sync_timer():
    """Desregistra el temporizador al desactivar el addon."""
    if bpy.app.timers.is_registered(check_and_reload_textures):
        bpy.app.timers.unregister(check_and_reload_textures)
