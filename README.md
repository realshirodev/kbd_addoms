# 🎨 Krita Live Texturing for Blender

[![Blender Version](https://img.shields.io/badge/Blender-4.0%2B-orange?logo=blender&logoColor=white)](https://www.blender.org/)
[![Krita](https://img.shields.io/badge/Krita-Compatible-blue?logo=krita&logoColor=white)](https://krita.org/)
[![Developer](https://img.shields.io/badge/Developer-ShiroDev-red?logo=youtube&logoColor=white)](https://www.youtube.com/@shiro_dev)

**Krita Live Texturing** es un complemento para Blender diseñado para acelerar y automatizar el flujo de trabajo de texturizado 2D en modelos 3D usando **Krita**. 

Exporta las UVs de tu modelo, genera un proyecto multicapa nativo y abre Krita automáticamente con un solo clic. Cada vez que guardas en Krita (`Ctrl + S`), la textura se actualiza instantáneamente en el visor 3D de Blender en tiempo real.

---

## ✨ Características Principales

- 🚀 **Flujo en 1 Clic**: Selecciona tu malla en Blender, haz clic en *Iniciar Proyecto en Krita* y el archivo se genera y abre automáticamente.
- 📑 **Proyecto Multicapa Nativo (.ORA)**:
  - **Capa `Pintura` (arriba)**: Capa vacía y transparente lista para que empieces a dibujar inmediatamente.
  - **Capa `UV Guide` (abajo)**: Mapa UV de tu modelo con opacidad suave para servir de guía sin estorbar tu arte.
- 🔄 **Sincronización en Tiempo Real**: Guarda en Krita con `Ctrl + S` y los cambios se reflejan de inmediato en el Viewport 3D de Blender (detección cada 0.3 segundos y redibujado automático).
- ⚙️ **Resoluciones Configurables**: Soporte directo para texturas en resoluciones **1K (1024x1024)**, **2K (2048x2048)** y **4K (4096x4096)**.
- 🎛️ **Configuración de Material Automática**: Crea o conecta automáticamente el nodo `ShaderNodeTexImage` al shader `Principled BSDF` del objeto activo.
- 📦 **Cero Dependencias Externas**: Funciona con librerías nativas de Python (sin requerir Pillow ni paquetes adicionales).

---

## 📋 Requisitos

- **Blender**: 4.0.0 o superior.
- **Krita**: Cualquier versión moderna instalada en tu sistema.

---

## 📥 Instalación

1. Descarga el repositorio o clónalo:
   ```bash
   git clone https://github.com/tu-usuario/kbd_addoms.git
   ```
2. Comprime la carpeta `kbd_addoms` en un archivo `.zip` (o descarga el release `.zip`).
3. En Blender, ve a **Edit > Preferences > Add-ons**.
4. Haz clic en **Install...** (o la flecha en la esquina superior derecha según la versión de Blender).
5. Selecciona el archivo `.zip` y activa la casilla de **Krita Live Texturing**.

---

## 🎮 Modo de Uso

1. En la vista 3D de Blender, presiona la tecla `N` para abrir la barra lateral y dirígete a la pestaña **Krita Sync**.
2. **Configuración**:
   - **Lienzo**: Selecciona la resolución deseada (`1K`, `2K`, `4K`).
   - **Ruta Krita**: Verifica que la ruta apunte al ejecutable de Krita en tu sistema (por defecto: `C:\Program Files\Krita (x64)\bin\krita.exe`).
3. Selecciona tu objeto tipo **MESH** (con sus UVs previamente desenvueltas/unwrapped).
4. Haz clic en **Iniciar Proyecto en Krita**.
5. Krita se abrirá automáticamente con las dos capas preparadas:
   - Dibuja sobre la capa **Pintura**.
   - Presiona **`Ctrl + S`** para guardar.
6. ¡Listo! Vuelve a Blender y verás la textura actualizada en tu modelo 3D al instante.

---

## 🏗️ Estructura del Código

```
kbd_addoms/
├── __init__.py           # Metadatos del addon y orquestador de registro
├── properties.py         # Propiedades de escena (resolución, rutas)
├── core/
│   ├── security.py       # Verificación de integridad y autoría
│   ├── ora_manager.py    # Generador de archivos OpenRaster (.ora) y PNGs
│   └── sync_timer.py     # Monitor en tiempo real para recarga automática
├── operators/
│   └── setup_krita.py    # Operador principal de exportación y enlace
└── ui/
    └── panel.py          # Interfaz de usuario en la barra lateral de View3D
```

---

## 👤 Desarrollador & Créditos

Creado y desarrollado por **ShiroDev**.

- 📺 **YouTube**: [@shiro_dev](https://www.youtube.com/@shiro_dev)

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.
