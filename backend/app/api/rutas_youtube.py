"""Rutas de descarga de YouTube."""
from fastapi import APIRouter, Response
from pydantic import BaseModel
from app.conversores.youtube import descargar_de_youtube

enrutador_youtube = APIRouter()

class SolicitudYouTube(BaseModel):
    url: str
    formato: str = "mp4"
    calidad: str = "best"

@enrutador_youtube.post("/descargar-youtube")
async def descargar_youtube(solicitud: SolicitudYouTube):
    """Descarga video o audio de YouTube usando yt-dlp."""
    bytes_archivo = descargar_de_youtube(solicitud.url, solicitud.formato)
    
    media_type = "audio/mpeg" if solicitud.formato == "mp3" else "video/mp4"
    return Response(content=bytes_archivo, media_type=media_type)
