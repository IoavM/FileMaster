"""
Eliminador de fondo.
Utiliza la librería rembg para eliminar el fondo de las imágenes automáticamente.
Importación perezosa: rembg y onnxruntime solo se cargan cuando se invoca la función.
"""

def remover_fondo_imagen(bytes_entrada: bytes) -> bytes:
    """
    Elimina el fondo de una imagen recibida en bytes y devuelve los bytes de la imagen resultante (PNG transparente).
    """
    from rembg import remove
    bytes_salida = remove(bytes_entrada)
    return bytes_salida
