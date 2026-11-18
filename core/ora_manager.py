import os
import zipfile
import struct
import zlib
import xml.etree.ElementTree as ET

def create_solid_png(filepath: str, width: int, height: int, r: int = 255, g: int = 255, b: int = 255, a: int = 255):
    """Crea un PNG con un color sólido sin dependencias externas (usando solo struct y zlib)."""
    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return struct.pack('>I', len(data)) + chunk + crc

    signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)

    pixel_bytes = bytes([r, g, b, a])
    raw_row = b'\x00' + (pixel_bytes * width)
    raw_data = raw_row * height
    compressed = zlib.compress(raw_data)
    idat = make_chunk(b'IDAT', compressed)
    iend = make_chunk(b'IEND', b'')

    # Asegurar que el directorio contenedor exista
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'wb') as f:
        f.write(signature + ihdr + idat + iend)


def create_transparent_png(filepath: str, width: int, height: int):
    """Crea un PNG completamente transparente."""
    create_solid_png(filepath, width, height, 0, 0, 0, 0)


def create_ora_file(ora_path: str, paint_layer_path: str, uv_layer_path: str, bg_layer_path: str, 
                    width: int, height: int, uv_opacity: float = 0.35, uv_visible: bool = True):
    """Crea un archivo OpenRaster (.ora) nativo para Krita con 3 capas:
       - Superior: 'Pintura' (vacía, donde el artista dibuja)
       - Intermedia: 'UV Guide' (guía de referencia)
       - Inferior: 'Fondo' (color configurado para evitar que el modelo se vea negro)
    """
    os.makedirs(os.path.dirname(ora_path), exist_ok=True)
    vis_str = "visible" if uv_visible else "hidden"
    opacity_clamped = max(0.0, min(1.0, float(uv_opacity)))

    stack_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<image version="0.0.3" w="{width}" h="{height}" xres="72" yres="72">
  <stack>
    <layer name="Pintura" src="data/paint.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over" />
    <layer name="UV Guide" src="data/uv_guide.png" x="0" y="0" opacity="{opacity_clamped:.2f}" visibility="{vis_str}" composite-op="svg:src-over" />
    <layer name="Fondo" src="data/background.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over" />
  </stack>
</image>'''

    with zipfile.ZipFile(ora_path, 'w', compression=zipfile.ZIP_DEFLATED) as ora:
        ora.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        ora.writestr("stack.xml", stack_xml)
        ora.write(paint_layer_path, "data/paint.png")
        ora.write(uv_layer_path, "data/uv_guide.png")
        ora.write(bg_layer_path, "data/background.png")
        ora.write(bg_layer_path, "mergedimage.png")
        ora.write(uv_layer_path, "Thumbnails/thumbnail.png")


def update_ora_uv_guide(ora_path: str, new_uv_layer_path: str) -> bool:
    """Actualiza la capa 'UV Guide' en un archivo .ora existente de forma no destructiva.
    
    Conserva todas las capas de pintura creadas por el artista en Krita.
    """
    if not os.path.exists(ora_path) or not os.path.exists(new_uv_layer_path):
        return False

    temp_zip = ora_path + ".tmp"
    uv_src_target = "data/uv_guide.png"

    try:
        with zipfile.ZipFile(ora_path, 'r') as zin:
            namelist = zin.namelist()

            # Intentar inspeccionar stack.xml para ver cómo nombró Krita la capa 'UV Guide'
            if "stack.xml" in namelist:
                try:
                    xml_content = zin.read("stack.xml")
                    root = ET.fromstring(xml_content)
                    for layer in root.iter("layer"):
                        if layer.attrib.get("name") == "UV Guide":
                            uv_src_target = layer.attrib.get("src", uv_src_target)
                            break
                except Exception:
                    pass

            with zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    # Omitir la capa UV previa y el thumbnail previo
                    if item.filename in (uv_src_target, "Thumbnails/thumbnail.png"):
                        continue
                    
                    # Conservar mimetype sin compresión como exige el estándar OpenRaster
                    if item.filename == "mimetype":
                        zout.writestr(item, zin.read(item.filename), compress_type=zipfile.ZIP_STORED)
                    else:
                        zout.writestr(item, zin.read(item.filename))

                # Escribir la nueva guía UV en la ruta correspondiente
                zout.write(new_uv_layer_path, uv_src_target)
                zout.write(new_uv_layer_path, "Thumbnails/thumbnail.png")

        # Reemplazar atómicamente el archivo original
        os.replace(temp_zip, ora_path)
        return True
    except Exception as e:
        if os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except Exception:
                pass
        raise e


def extract_composite_from_ora(ora_path: str, output_png_path: str) -> bool:
    """Extrae 'mergedimage.png' de un archivo .ora y lo guarda en disco."""
    if not os.path.exists(ora_path):
        return False
    try:
        with zipfile.ZipFile(ora_path, 'r') as zf:
            if "mergedimage.png" in zf.namelist():
                data = zf.read("mergedimage.png")
                os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
                with open(output_png_path, 'wb') as f:
                    f.write(data)
                return True
    except Exception:
        pass
    return False
