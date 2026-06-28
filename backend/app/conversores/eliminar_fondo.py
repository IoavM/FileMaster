"""
Eliminador de fondo.
Utiliza la librería rembg para eliminar el fondo de las imágenes automáticamente.
"""
from rembg import remove

def remover_fondo_imagen(bytes_entrada: bytes) -> bytes:
    """
    Elimina el fondo de una imagen recibida en bytes y devuelve los bytes de la imagen resultante (PNG transparente).
    """
    bytes_salida = remove(bytes_entrada)
    return bytes_salida
