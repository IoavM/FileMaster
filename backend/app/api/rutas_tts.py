"""Rutas de texto a voz."""
from fastapi import APIRouter, Response
from pydantic import BaseModel
from app.conversores.texto_a_voz import generar_audio_tts

enrutador_tts = APIRouter()

class SolicitudTTS(BaseModel):
    texto: str
    voz: str = "es-MX-DaliaNeural"
    velocidad: float = 1.0

@enrutador_tts.post("/texto-a-voz")
async def texto_a_voz(solicitud: SolicitudTTS):
    """Convierte texto a audio usando edge-tts."""
    audio_bytes = await generar_audio_tts(
        texto=solicitud.texto,
        voz=solicitud.voz,
        velocidad=solicitud.velocidad
    )
    return Response(content=audio_bytes, media_type="audio/mpeg")
