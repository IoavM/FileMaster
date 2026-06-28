"""Rutas de conversión de archivos."""
import os
from fastapi import APIRouter, Response, UploadFile, File, Form, HTTPException

from app.conversores.imagenes import convertir_imagen
from app.conversores.audio import convertir_audio
from app.conversores.video import convertir_video
from app.conversores.documentos import convertir_documento

enrutador_conversion = APIRouter()

FORMATOS_IMAGEN = ('png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'tiff', 'svg')
FORMATOS_AUDIO = ('mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a')
FORMATOS_VIDEO = ('mp4', 'avi', 'mov', 'webm', 'mkv')
FORMATOS_DOCUMENTO = ('pdf', 'docx', 'xlsx', 'txt', 'csv')

@enrutador_conversion.post("/convertir")
async def convertir(
    archivo: UploadFile = File(...),
    formato_salida: str = Form(...),
):
    """Convierte un archivo al formato de salida especificado."""
    nombre_archivo = archivo.filename if archivo.filename else ""
    partes = nombre_archivo.split('.')
    if len(partes) < 2:
        raise HTTPException(status_code=400, detail="El archivo no tiene una extensión válida.")
        
    ext_entrada = partes[-1].lower()
    ext_salida = formato_salida.lower()
    bytes_entrada = await archivo.read()
    
    try:
        # 1. Conversión de Imágenes
        if ext_entrada in FORMATOS_IMAGEN and ext_salida in FORMATOS_IMAGEN:
            bytes_salida = convertir_imagen(bytes_entrada, ext_salida)
            media_type = f"image/{ext_salida}"
            if ext_salida == "jpg":
                media_type = "image/jpeg"
            return Response(content=bytes_salida, media_type=media_type)
            
        # 2. Conversión de Audio
        elif ext_entrada in FORMATOS_AUDIO and ext_salida in FORMATOS_AUDIO:
            bytes_salida = convertir_audio(bytes_entrada, ext_entrada, ext_salida)
            media_type = f"audio/{ext_salida}"
            if ext_salida == "mp3":
                media_type = "audio/mpeg"
            return Response(content=bytes_salida, media_type=media_type)
            
        # 3. Conversión de Video
        elif ext_entrada in FORMATOS_VIDEO and ext_salida in FORMATOS_VIDEO:
            bytes_salida = convertir_video(bytes_entrada, ext_salida)
            media_type = f"video/{ext_salida}"
            return Response(content=bytes_salida, media_type=media_type)
            
        # 4. Conversión de Documentos (incluye exportar PDF a imagen)
        elif (ext_entrada in FORMATOS_DOCUMENTO and ext_salida in FORMATOS_DOCUMENTO) or \
             (ext_entrada == "pdf" and ext_salida in FORMATOS_IMAGEN):
            bytes_salida = convertir_documento(bytes_entrada, ext_entrada, ext_salida)
            
            if ext_entrada == "pdf" and ext_salida in FORMATOS_IMAGEN and len(bytes_salida) > 0:
                if bytes_salida.startswith(b'PK'):
                    return Response(
                        content=bytes_salida,
                        media_type="application/zip",
                        headers={"Content-Disposition": "attachment; filename=paginas_imagen.zip"}
                    )
            
            if ext_salida == "pdf":
                media_type = "application/pdf"
            elif ext_salida == "docx":
                media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext_salida == "xlsx":
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif ext_salida == "txt":
                media_type = "text/plain"
            elif ext_salida == "csv":
                media_type = "text/csv"
            else:
                media_type = f"image/{ext_salida}"
                
            return Response(content=bytes_salida, media_type=media_type)
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Conversión no soportada de .{ext_entrada} a .{ext_salida}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en la conversión: {str(e)}"
        )
