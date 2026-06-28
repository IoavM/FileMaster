"""Rutas de generación de códigos QR."""
from fastapi import APIRouter, Response
from pydantic import BaseModel
from app.conversores.codigo_qr import generar_codigo_qr

enrutador_qr = APIRouter()

class SolicitudQR(BaseModel):
    contenido: str
    tamano: int = 300
    color: str = "#000000"
    fondo: str = "#FFFFFF"

@enrutador_qr.post("/generar-qr")
async def generar_qr(solicitud: SolicitudQR):
    """Genera un código QR personalizado."""
    img_bytes = generar_codigo_qr(
        contenido=solicitud.contenido,
        tamano=solicitud.tamano,
        color=solicitud.color,
        fondo=solicitud.fondo
    )
    return Response(content=img_bytes, media_type="image/png")
