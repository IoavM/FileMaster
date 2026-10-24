"""Rutas de compresión de imágenes con validación y sanitización defensiva."""
import logging
from fastapi import APIRouter, Response, UploadFile, File, Form, HTTPException
from app.conversores.compresor import comprimir_imagen_pillow

logger = logging.getLogger("filemaster.compresor")
enrutador_compresor = APIRouter()


@enrutador_compresor.post("/comprimir")
async def comprimir_imagen(
    archivo: UploadFile = File(...),
    calidad: int = Form(80),
):
    """Comprime una imagen con la calidad especificada y manejo seguro de errores."""
    if calidad < 1 or calidad > 100:
        raise HTTPException(status_code=400, detail="La calidad debe encontrarse entre 1 y 100.")

    try:
        bytes_entrada = await archivo.read()
        if not bytes_entrada:
            raise HTTPException(status_code=400, detail="El archivo subido está vacío.")

        bytes_salida = comprimir_imagen_pillow(bytes_entrada, calidad)
        ext = archivo.filename.split('.')[-1].lower() if archivo.filename else 'jpg'
        media_type = f"image/{ext}" if ext in ('png', 'webp', 'gif') else "image/jpeg"
        return Response(content=bytes_salida, media_type=media_type)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error comprimiendo imagen: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al comprimir la imagen.")
