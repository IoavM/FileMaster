"""
Texto a voz (TTS).
Utiliza edge-tts para convertir texto en audio MP3 con voces naturales de Microsoft.
"""
import edge_tts

async def generar_audio_tts(texto: str, voz: str = "es-MX-DaliaNeural", velocidad: float = 1.0) -> bytes:
    """
    Convierte texto a voz y devuelve los bytes del archivo de audio MP3.
    """
    # Formatear la velocidad en el formato esperado por edge-tts (ej: "+10%" o "-15%")
    porcentaje = int((velocidad - 1.0) * 100)
    rate = f"{'+' if porcentaje >= 0 else ''}{porcentaje}%"
    
    comunicador = edge_tts.Communicate(texto, voz, rate=rate)
    
    bytes_audio = bytearray()
    async for fragmento in comunicador.stream():
        if fragmento["type"] == "audio":
            bytes_audio.extend(fragmento["data"])
            
    return bytes(bytes_audio)
