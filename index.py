# Krita Live Texturing - Lanzador de compatibilidad
# Desarrollador: ShiroDev (https://www.youtube.com/@shiro_dev)

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

import __init__ as kbd_addon

bl_info = kbd_addon.bl_info

def register():
    kbd_addon.register()

def unregister():
    kbd_addon.unregister()

if __name__ == "__main__":
    register()