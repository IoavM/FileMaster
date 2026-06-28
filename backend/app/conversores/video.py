"""
Conversor de video.
Usa subprocess para ejecutar ffmpeg de forma directa y convertir videos entre MP4, AVI, MOV, WEBM, etc.
"""
import subprocess
import tempfile
import os

def convertir_video(bytes_entrada: bytes, formato_salida: str) -> bytes:
    """
    Convierte un video en bytes al formato de salida especificado.
    Usa ffmpeg para la transcodificación.
    """
    formato_salida = formato_salida.lower()
    
    with tempfile.TemporaryDirectory() as dir_temp:
        ruta_entrada = os.path.join(dir_temp, "entrada_video")
        ruta_salida = os.path.join(dir_temp, f"salida_video.{formato_salida}")
        
        with open(ruta_entrada, "wb") as f:
            f.write(bytes_entrada)
            
        comando = ["ffmpeg", "-y", "-i", ruta_entrada]
        
        # Parámetros optimizados por velocidad para Render
        if formato_salida == "mp4":
            comando.extend(["-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-strict", "experimental"])
        elif formato_salida == "webm":
            comando.extend(["-c:v", "libvpx", "-preset", "ultrafast", "-c:a", "libvorbis"])
        elif formato_salida == "avi":
            comando.extend(["-c:v", "libxvid", "-c:a", "mp3"])
        
        comando.append(ruta_salida)
        
        resultado = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if resultado.returncode != 0:
            raise RuntimeError(f"Error al ejecutar ffmpeg: {resultado.stderr}")
            
        with open(ruta_salida, "rb") as f:
            return f.read()
