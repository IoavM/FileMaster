"""
Descargador de YouTube.
Utiliza yt-dlp para descargar videos y audios de YouTube en formatos MP4 y MP3.
"""
import os
import tempfile
import yt_dlp

def descargar_de_youtube(url: str, formato: str = "mp4") -> bytes:
    """
    Descarga un video o audio de YouTube y devuelve los bytes del archivo resultante.
    Soporta formato="mp4" (video) y formato="mp3" (audio).
    """
    with tempfile.TemporaryDirectory() as dir_temp:
        plantilla_salida = os.path.join(dir_temp, "descarga.%(ext)s")
        
        if formato == "mp3":
            opciones = {
                'format': 'bestaudio/best',
                'outtmpl': plantilla_salida,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
        else:
            opciones = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': plantilla_salida,
                'quiet': True,
                'no_warnings': True,
            }
            
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
            
        archivos = os.listdir(dir_temp)
        if not archivos:
            raise RuntimeError("No se generó ningún archivo en la descarga.")
            
        ruta_archivo = os.path.join(dir_temp, archivos[0])
        with open(ruta_archivo, "rb") as f:
            return f.read()
