"""Rutas de generación de códigos QR con validación y sanitización."""
import logging
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field
from app.conversores.codigo_qr import generar_codigo_qr

logger = logging.getLogger("filemaster.qr")
enrutador_qr = APIRouter()


class SolicitudQR(BaseModel):
    contenido: str = Field(..., min_length=1, max_length=2048, description="Texto o URL para codificar")
    tamano: int = Field(300, ge=50, le=2000, description="Tamaño en píxeles")
    color: str = Field("#000000", max_length=30)
    fondo: str = Field("#FFFFFF", max_length=30)


@enrutador_qr.post("/generar-qr")
async def generar_qr(solicitud: SolicitudQR):
    """Genera un código QR personalizado de forma segura."""
    if not solicitud.contenido.strip():
        raise HTTPException(status_code=400, detail="El contenido para el código QR no puede estar vacío.")

    try:
        img_bytes = generar_codigo_qr(
            contenido=solicitud.contenido,
            tamano=solicitud.tamano,
            color=solicitud.color,
            fondo=solicitud.fondo
        )
        return Response(content=img_bytes, media_type="image/png")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generando código QR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al generar el código QR.")
