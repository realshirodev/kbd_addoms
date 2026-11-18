import bpy
import os
import zipfile

last_modified_times = {}

def check_and_reload_textures():
    """Timer periódico de Blender que detecta cuando Krita guarda y recarga en tiempo real."""
    # Comprobar si la sincronización está activa
    sync_active = True
    sync_interval = 0.3
    auto_pack = False

    try:
        scene = bpy.context.scene
        if scene:
            sync_active = getattr(scene, "krita_sync_active", True)
            sync_interval = max(0.1, min(3.0, getattr(scene, "krita_sync_interval", 0.3)))
            auto_pack = getattr(scene, "krita_auto_pack", True)
    except Exception:
        pass

    if not sync_active:
        return sync_interval

    for img in list(bpy.data.images):
        if img.source != 'FILE' or not img.filepath:
            continue

        abs_path = os.path.normpath(bpy.path.abspath(img.filepath))
        
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
                            # Escribir la imagen compuesta al archivo PNG de Blender
                            with open(abs_path, 'wb') as f:
                                f.write(data)
                except (zipfile.BadZipFile, PermissionError, OSError):
                    # Si Krita aún está escribiendo en disco, esperar al siguiente ciclo
                    continue

            last_modified_times[file_to_track] = mtime
            
            # Recargar y actualizar datos en memoria GPU de Blender
            try:
                img.reload()
                if hasattr(img, "update"):
                    img.update()
            except Exception:
                pass

            # Si el usuario tiene activo 'Empaquetar en .blend', incrustar datos en el archivo
            if auto_pack:
                try:
                    img.pack()
                except Exception:
                    pass

            # Forzar refresco inmediato del Viewport 3D y del Image Editor (UV Editor)
            try:
                wm = getattr(bpy.context, "window_manager", None)
                if wm and hasattr(wm, "windows"):
                    for window in wm.windows:
                        if hasattr(window, "screen") and window.screen:
                            for area in window.screen.areas:
                                if area.type in ('VIEW_3D', 'IMAGE_EDITOR'):
                                    area.tag_redraw()
            except Exception:
                pass

            print(f"[Krita-Sync] Textura recargada automáticamente: {img.name}")

    return sync_interval


def start_sync_timer():
    """Registra el temporizador si no está activo."""
    if not bpy.app.timers.is_registered(check_and_reload_textures):
        bpy.app.timers.register(check_and_reload_textures, persistent=True)


def stop_sync_timer():
    """Desregistra el temporizador al desactivar el addon."""
    if bpy.app.timers.is_registered(check_and_reload_textures):
        bpy.app.timers.unregister(check_and_reload_textures)
