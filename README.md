# 🎨 Krita Live Texturing for Blender

[![Blender Version](https://img.shields.io/badge/Blender-4.0%20a%205.3%2B-orange?logo=blender&logoColor=white)](https://www.blender.org/)
[![Extensions Platform](https://img.shields.io/badge/Blender%20Extensions-Compatible-green?logo=blender&logoColor=white)](https://extensions.blender.org/)
[![Krita](https://img.shields.io/badge/Krita-Compatible-blue?logo=krita&logoColor=white)](https://krita.org/)
[![Developer](https://img.shields.io/badge/Developer-ShiroDev-red?logo=youtube&logoColor=white)](https://www.youtube.com/@shiro_dev)
[![Website](https://img.shields.io/badge/Website-Team%20Apricot-success?logo=google-chrome&logoColor=white)](https://teamapricot.com/marketplace/krita-live-texturing-for-blender)

**Krita Live Texturing** es un complemento y extensión profesional para Blender diseñado para acelerar y automatizar el flujo de trabajo de texturizado 2D/3D utilizando **Krita**. 

Exporta el mapeado UV de tu modelo, genera proyectos multicapa nativos de Krita (`.ora`), gestiona la persistencia segura de tus texturas para no perder tu trabajo y sincroniza en tiempo real cada guardado (`Ctrl + S`) directamente en el visor 3D de Blender.

---

## ✨ Características Principales

- 🚀 **Flujo de Trabajo Inmediato**: Selecciona tu malla en Blender, haz clic en *Iniciar / Abrir en Krita* y tu proyecto se genera y abre al instante.
- 💾 **Persistencia Total (¡Cero Pérdida de Texturas!)**:
  - **Junto al archivo .blend (Recomendado)**: Guarda las texturas y el proyecto `.ora` en una subcarpeta (por defecto `textures/`) relativa a tu proyecto 3D.
  - **Carpeta personalizada**: Permite definir cualquier carpeta en tu disco o red.
  - **Auto-Empaquetado en .blend**: Incrusta automáticamente los datos de la textura dentro del archivo `.blend` (`img.pack()`), garantizando que la textura nunca se pierda ni aparezca en color magenta/rosa al mover o compartir el archivo.
  - **Protección No Destructiva**: Si el proyecto ya existe, lo abre en Krita sin borrar ni reiniciar tus capas de arte previas.
- 🔄 **Actualización de Guía UV No Destructiva**: Si modificas las UVs de tu modelo en Blender, utiliza el botón *Actualizar UV* para reemplazar únicamente la capa de guía en tu `.ora` existente sin tocar tus capas de pintura.
- 🎨 **Soporte PBR Multicanal**:
  - **Color Base (Albedo)**: Espacio de color sRGB conectado a Base Color.
  - **Rugosidad (Roughness)**: Espacio Non-Color conectado a Roughness.
  - **Metálico (Metallic)**: Espacio Non-Color conectado a Metallic.
  - **Mapa de Normales (Normal Map)**: Espacio Non-Color conectado a través de un nodo `ShaderNodeNormalMap`.
  - **Emisión (Emission)**: Espacio sRGB conectado a Emission Color.
- 📑 **Proyecto Multicapa Nativo OpenRaster (.ora)**:
  - **Capa `Pintura`**: Capa transparente lista para empezar a pintar.
  - **Capa `UV Guide`**: Mapa UV con opacidad y visibilidad ajustables.
  - **Capa `Fondo`**: Color seleccionable (Blanco, Gris neutro 50%, Negro o Transparente).
- 🔄 **Sincronización en Tiempo Real**: Guarda en Krita (`Ctrl + S`) y la textura se recarga de inmediato en Blender (intervalo configurable, por defecto cada 0.3s) con redibujado automático de Viewport y UV Editor.
- ⚙️ **Resoluciones de Lienzo**: Soporte directo para **512px**, **1K (1024x1024)**, **2K (2048x2048)**, **4K (4096x4096)** y **8K (8192x8192)**.
- 🔍 **Auto-Detección de Krita**: Detecta automáticamente la instalación de Krita en Windows, macOS y Linux.
- 📦 **Cero Dependencias Externas**: Funciona con librerías nativas de Python (sin requerir Pillow ni paquetes pip adicionales).
- 🧩 **Soporte Moderno de Extensiones**: Totalmente compatible con la nueva arquitectura de **Blender Extensions** (`blender_manifest.toml`) y compatible desde Blender 4.0 hasta **Blender 5.0, 5.2 y 5.3+**.

---

## 📋 Requisitos

- **Blender**: 4.0.0 o superior (compatible con Blender 4.2 LTS, 4.3, 5.0, 5.2, 5.3+).
- **Krita**: Cualquier versión moderna instalada en tu sistema (5.x recomendada).

---

## 📥 Instalación

### Método 1: Blender 4.2+ y 5.x (Plataforma de Extensiones)
1. Comprime el contenido de la carpeta del addon en un archivo `.zip`.
2. En Blender, ve a **Edit > Preferences > Get Extensions** (o la flecha superior derecha en Preferences).
3. Selecciona **Install from Disk...** y elige tu archivo `.zip`.

### Método 2: Blender 4.0 - 4.1 (Addons Tradicionales)
1. En Blender, ve a **Edit > Preferences > Add-ons**.
2. Haz clic en **Install...**, selecciona el archivo `.zip` y activa la casilla **Krita Live Texturing**.

---

## 🎮 Modo de Uso

1. En la vista 3D de Blender, presiona la tecla `N` para abrir la barra lateral y dirígete a la pestaña **Krita Sync**.
2. **Almacenamiento**:
   - Selecciona **Junto al archivo .blend** (asegúrate de haber guardado tu `.blend` con `Ctrl + S`).
   - Mantén activada la opción **Auto-empaquetar en .blend** para mayor seguridad.
3. **Configuración de Lienzo**:
   - Selecciona el canal (por ejemplo `Color Base`).
   - Elige la resolución deseada (`1K`, `2K`, `4K`, etc.).
   - Ajusta el color de fondo y la opacidad de la guía UV si lo deseas.
4. Selecciona tu objeto tipo **MESH** (con sus UVs previamente desenvueltas).
5. Haz clic en **Iniciar / Abrir en Krita**.
6. Krita se abrirá automáticamente con las capas preparadas:
   - Dibuja sobre la capa **Pintura** (o crea nuevas capas en Krita).
   - Presiona **`Ctrl + S`** para guardar en Krita.
7. ¡Listo! Vuelve a Blender y verás la textura actualizada en tu modelo 3D al instante.

---

## 🛠️ Herramientas Adicionales

- **Actualizar UV**: Si editas las costuras UV o haces un nuevo Unwrap, pulsa este botón para actualizar la guía en el proyecto `.ora` sin perder tu pintura.
- **Empaquetar .blend**: Incrusta la textura en el `.blend` para portabilidad completa.
- **Guardar a Disco**: Guarda inmediatamente el archivo PNG a la carpeta configurada.
- **Abrir Carpeta**: Abre la carpeta de texturas en el Explorador de Archivos de tu sistema operativo.
- **Pausar / Reanudar Sincronización**: Permite pausar la comprobación periódica en escenas muy pesadas.

---

## 🏗️ Estructura del Código

```
kbd_addoms/
├── blender_manifest.toml # Manifiesto para el nuevo sistema de Extensiones de Blender 4.2+ / 5.x
├── __init__.py           # Metadatos del addon y orquestador de registro
├── properties.py         # Propiedades de escena (almacenamiento, canales, resolución)
├── core/
│   ├── paths.py          # Resolución inteligente de rutas, persistencia y auto-detección de Krita
│   ├── security.py       # Verificación de integridad criptográfica y autoría
│   ├── ora_manager.py    # Generador y actualizador no destructivo de archivos OpenRaster (.ora)
│   └── sync_timer.py     # Monitor en tiempo real para recarga y auto-empaquetado
├── operators/
│   ├── __init__.py       # Registro de operadores
│   ├── setup_krita.py    # Operador principal de creación, enlace PBR y apertura
│   └── extra_ops.py      # Operadores de actualización UV, empaquetado y utilidades
└── ui/
    └── panel.py          # Interfaz de usuario completa en la barra lateral de View3D
```

---

## 👤 Desarrollador & Créditos

Creado y desarrollado por **ShiroDev**.

- 📺 **YouTube**: [@shiro_dev](https://www.youtube.com/@shiro_dev)
- 🌐 **Sitio Web**: [teamapricot.com](https://teamapricot.com)
- 🛒 **Página Oficial**: [Krita Live Texturing en Team Apricot](https://teamapricot.com/marketplace/krita-live-texturing-for-blender)

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.
