"""
Generador de códigos QR.
Usa la librería qrcode para generar códigos QR personalizados en formato PNG.
"""
import qrcode
from io import BytesIO

def generar_codigo_qr(contenido: str, tamano: int = 300, color: str = "#000000", fondo: str = "#FFFFFF") -> bytes:
    """
    Genera un código QR con el contenido especificado y los colores dados.
    Devuelve los bytes de la imagen PNG.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(contenido)
    qr.make(fit=True)

    img = qr.make_image(fill_color=color, back_color=fondo)
    
    img = img.resize((tamano, tamano))
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
