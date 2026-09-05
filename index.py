# Krita Live Texturing - Lanzador de compatibilidad
# Desarrollado por: ShiroDev (https://www.youtube.com/@shiro_dev)

import os
import sys

# Añadir el directorio actual al path para resolución de paquetes si se ejecuta desde Text Editor
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from . import bl_info, register, unregister

if __name__ == "__main__":
    register()