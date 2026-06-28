"""Rutas de compresión de imágenes."""
from fastapi import APIRouter, Response, UploadFile, File, Form
from app.conversores.compresor import comprimir_imagen_pillow

enrutador_compresor = APIRouter()

@enrutador_compresor.post("/comprimir")
async def comprimir_imagen(
    archivo: UploadFile = File(...),
    calidad: int = Form(80),
):
    """Comprime una imagen con la calidad especificada."""
    bytes_entrada = await archivo.read()
    bytes_salida = comprimir_imagen_pillow(bytes_entrada, calidad)
    
    ext = archivo.filename.split('.')[-1].lower() if archivo.filename else 'jpg'
    media_type = f"image/{ext}" if ext in ('png', 'webp', 'gif') else "image/jpeg"
    
    return Response(content=bytes_salida, media_type=media_type)
