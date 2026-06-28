"""
Compresor de imágenes.
Utiliza Pillow para reducir el peso de las imágenes optimizándolas y ajustando su calidad.
"""
from io import BytesIO
from PIL import Image

def comprimir_imagen_pillow(bytes_entrada: bytes, calidad: int = 80) -> bytes:
    """
    Comprime una imagen en bytes con la calidad dada (1-100) y devuelve la imagen optimizada.
    Mantiene el formato original si es posible.
    """
    img = Image.open(BytesIO(bytes_entrada))
    formato = img.format if img.format else "JPEG"
    
    buffer = BytesIO()
    
    if formato == "PNG":
        # PNG usa compresión sin pérdida, por lo que 'quality' no aplica igual.
        img.save(buffer, format="PNG", optimize=True)
    elif formato == "WEBP":
        img.save(buffer, format="WEBP", quality=calidad, method=6)
    else:
        # Para JPEG u otros formatos convertimos a RGB si es RGBA
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            # Si es JPEG no soporta canal alpha, convertimos a RGB con fondo blanco
            fondo = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                fondo.paste(img, mask=img.split()[3])
            else:
                fondo.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[3])
            img = fondo
        elif img.mode != "RGB":
            img = img.convert("RGB")
            
        img.save(buffer, format="JPEG", quality=calidad, optimize=True)
        
    return buffer.getvalue()
