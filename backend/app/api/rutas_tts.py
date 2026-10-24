"""Rutas de texto a voz con validación y sanitización defensiva."""
import logging
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field
from app.conversores.texto_a_voz import generar_audio_tts

logger = logging.getLogger("filemaster.tts")
enrutador_tts = APIRouter()


class SolicitudTTS(BaseModel):
    texto: str = Field(..., min_length=1, max_length=15000, description="Texto a sintetizar en voz")
    voz: str = Field("es-MX-DaliaNeural", max_length=64)
    velocidad: float = Field(1.0, ge=0.5, le=2.0)


@enrutador_tts.post("/texto-a-voz")
async def texto_a_voz(solicitud: SolicitudTTS):
    """Convierte texto a audio usando edge-tts con control de errores."""
    if not solicitud.texto.strip():
        raise HTTPException(status_code=400, detail="El texto para síntesis no puede estar vacío.")

    try:
        audio_bytes = await generar_audio_tts(
            texto=solicitud.texto,
            voz=solicitud.voz,
            velocidad=solicitud.velocidad
        )
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generando audio TTS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al generar el archivo de audio.")
