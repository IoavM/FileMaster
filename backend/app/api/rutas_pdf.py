"""
Rutas de edición de PDF.
Protegidas con rate limiting defensivo contra fuerza bruta, validación de contraseñas y sanitización de errores.
"""
import json
import logging
from typing import List
from fastapi import APIRouter, Response, UploadFile, File, Form, HTTPException, Request

from app.configuracion.ajustes import configuracion
from app.utilidades.seguridad import limitador_tasa
from app.conversores.pdf import procesar_pdf

logger = logging.getLogger("filemaster.pdf")
enrutador_pdf = APIRouter()


@enrutador_pdf.post("/editar-pdf")
async def editar_pdf(
    request: Request,
    archivos: List[UploadFile] = File(...),
    operacion: str = Form(...),
    opciones: str = Form("{}"),
):
    """Edita archivos PDF con protecciones de seguridad activas."""
    # Mitigación estricta de fuerza bruta si la operación es desbloquear PDF
    if operacion == "desbloquear":
        ip_cliente = request.headers.get("x-forwarded-for")
        ip = ip_cliente.split(",")[0].strip() if ip_cliente else (request.client.host if request.client else "127.0.0.1")
        permitido, reintentar_en = limitador_tasa.verificar_limite(
            identificador=ip,
            operacion="desbloqueo_pdf",
            max_peticiones=configuracion.TASA_LIMITE_SENSIBLE,
            ventana_segundos=60.0,
        )
        if not permitido:
            logger.warning(f"Fuerza bruta mitigada en desbloqueo PDF para IP: {ip}")
            raise HTTPException(
                status_code=429,
                detail=f"Demasiados intentos de desbloqueo. Por favor espera {reintentar_en} segundos antes de reintentar.",
                headers={"Retry-After": str(reintentar_en)}
            )

    lista_bytes = []
    for archivo in archivos:
        bytes_archivo = await archivo.read()
        lista_bytes.append(bytes_archivo)

    try:
        dict_opciones = json.loads(opciones)
    except Exception:
        dict_opciones = {}

    try:
        bytes_salida = procesar_pdf(lista_bytes, operacion, dict_opciones)
    except ValueError as e:
        # Errores de validación controlados (contraseña incorrecta, débil, parámetros faltantes)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Error 500 sanitizado: registrar detalle real en servidor sin filtrar trazas al cliente
        logger.error(f"Falla interna al procesar operación PDF '{operacion}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno procesando el archivo PDF."
        )

    PARTICIPIOS_PDF = {
        "unir": "unido",
        "dividir": "dividido",
        "comprimir": "comprimido",
        "rotar": "rotado",
        "proteger": "protegido",
        "desbloquear": "desbloqueado",
        "ordenar": "ordenado",
        "firmar": "firmado",
        "traducir": "traducido",
    }
    participio = PARTICIPIOS_PDF.get(operacion, operacion)

    if operacion == "dividir":
        if "desde" in dict_opciones or "hasta" in dict_opciones:
            return Response(
                content=bytes_salida,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=archivo-dividido.pdf"}
            )
        return Response(
            content=bytes_salida,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=paginas-divididas.zip"}
        )

    return Response(
        content=bytes_salida,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=archivo-{participio}.pdf"}
    )
