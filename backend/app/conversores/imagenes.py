"""
Conversor de imágenes.
Soporta: JPG, PNG, WEBP, BMP, GIF, TIFF, SVG → múltiples formatos.
Usa Pillow para realizar la conversión de formatos.
"""
from io import BytesIO
from PIL import Image

def convertir_imagen(bytes_entrada: bytes, formato_salida: str) -> bytes:
    """
    Convierte una imagen de cualquier formato soportado por Pillow al formato_salida especificado.
    Devuelve los bytes de la imagen convertida.
    """
    img = Image.open(BytesIO(bytes_entrada))
    formato_salida = formato_salida.upper()
    
    # Mapeo de extensiones comunes a nombres de formatos de Pillow
    if formato_salida == "JPG":
        formato_salida = "JPEG"
        
    if formato_salida == "JPEG" and img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        fondo = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            fondo.paste(img, mask=img.split()[3])
        else:
            fondo.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[3])
        img = fondo
    elif img.mode != "RGB" and formato_salida == "JPEG":
        img = img.convert("RGB")
        
    buffer = BytesIO()
    img.save(buffer, format=formato_salida)
    return buffer.getvalue()
