import os
import zipfile
import struct
import zlib

def create_solid_png(filepath: str, width: int, height: int, r: int = 255, g: int = 255, b: int = 255, a: int = 255):
    """Crea un PNG con un color sólido (por defecto blanco) sin librerías externas."""
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

    with open(filepath, 'wb') as f:
        f.write(signature + ihdr + idat + iend)

def create_transparent_png(filepath: str, width: int, height: int):
    """Crea un PNG completamente transparente."""
    create_solid_png(filepath, width, height, 0, 0, 0, 0)

def create_ora_file(ora_path: str, paint_layer_path: str, uv_layer_path: str, bg_layer_path: str, width: int, height: int):
    """Crea un archivo OpenRaster (.ora) nativo para Krita con 3 capas:
       - Superior: 'Pintura' (vacía, donde el artista dibuja)
       - Intermedia: 'UV Guide' (guía de referencia)
       - Inferior: 'Fondo' (blanco sólido para evitar que el modelo se vea negro)
    """
    stack_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<image version="0.0.3" w="{width}" h="{height}" xres="72" yres="72">
  <stack>
    <layer name="Pintura" src="data/paint.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over" />
    <layer name="UV Guide" src="data/uv_guide.png" x="0" y="0" opacity="0.35" visibility="visible" composite-op="svg:src-over" />
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
