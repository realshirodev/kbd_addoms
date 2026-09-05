import os
import zipfile
import struct
import zlib

def create_transparent_png(filepath: str, width: int, height: int):
    """Crea un PNG completamente transparente sin requerir librerías externas."""
    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return struct.pack('>I', len(data)) + chunk + crc

    # Cabecera estándar PNG
    signature = b'\x89PNG\r\n\x1a\n'
    # IHDR: width, height, bit_depth=8, color_type=6 (RGBA)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)
    # IDAT: filas de píxeles RGBA (0,0,0,0) con byte de filtro 0
    raw_row = b'\x00' + (b'\x00\x00\x00\x00' * width)
    raw_data = raw_row * height
    compressed = zlib.compress(raw_data)
    idat = make_chunk(b'IDAT', compressed)
    # IEND
    iend = make_chunk(b'IEND', b'')

    with open(filepath, 'wb') as f:
        f.write(signature + ihdr + idat + iend)

def create_ora_file(ora_path: str, paint_layer_path: str, uv_layer_path: str, width: int, height: int):
    """Crea un archivo OpenRaster (.ora) nativo para Krita con:
       - Capa inferior: 'UV Guide' (guía de referencia)
       - Capa superior: 'Pintura' (capa vacía para dibujar)
    """
    # En OpenRaster (stack.xml), el orden de lectura es bottom-to-top (de abajo hacia arriba)
    stack_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<image version="0.0.3" w="{width}" h="{height}" xres="72" yres="72">
  <stack>
    <layer name="UV Guide" src="data/uv_guide.png" x="0" y="0" opacity="0.3" visibility="visible" composite-op="svg:src-over" />
    <layer name="Pintura" src="data/paint.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over" />
  </stack>
</image>'''

    with zipfile.ZipFile(ora_path, 'w', compression=zipfile.ZIP_DEFLATED) as ora:
        # El archivo mimetype debe ser el primero y sin compresión (ZIP_STORED)
        ora.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        ora.writestr("stack.xml", stack_xml)
        ora.write(uv_layer_path, "data/uv_guide.png")
        ora.write(paint_layer_path, "data/paint.png")
        # Vista previa inicial
        ora.write(paint_layer_path, "mergedimage.png")
        # Miniatura
        ora.write(uv_layer_path, "Thumbnails/thumbnail.png")
