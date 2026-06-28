"""Rutas de eliminación de fondo de imágenes."""
from fastapi import APIRouter, Response, UploadFile, File
from app.conversores.eliminar_fondo import remover_fondo_imagen

enrutador_fondo = APIRouter()

@enrutador_fondo.post("/eliminar-fondo")
async def eliminar_fondo(archivo: UploadFile = File(...)):
    """Elimina el fondo de una imagen usando rembg."""
    bytes_entrada = await archivo.read()
    bytes_salida = remover_fondo_imagen(bytes_entrada)
    return Response(content=bytes_salida, media_type="image/png")
