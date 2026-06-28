"""
Conversor de audio.
Usa pydub y ffmpeg para convertir archivos de audio entre formatos MP3, WAV, OGG, FLAC, AAC, etc.
"""
from io import BytesIO
from pydub import AudioSegment

def convertir_audio(bytes_entrada: bytes, formato_entrada: str, formato_salida: str) -> bytes:
    """
    Convierte un audio en bytes de un formato de entrada a un formato de salida.
    Devuelve los bytes del archivo resultante.
    """
    # Mapeos de formatos si es necesario
    formato_entrada = formato_entrada.lower()
    formato_salida = formato_salida.lower()
    
    # Cargar segmento de audio
    audio = AudioSegment.from_file(BytesIO(bytes_entrada), format=formato_entrada)
    
    buffer = BytesIO()
    audio.export(buffer, format=formato_salida)
    return buffer.getvalue()
