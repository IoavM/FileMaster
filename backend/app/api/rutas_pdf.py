"""Rutas de edición de PDF."""
import json
from fastapi import APIRouter, Response, UploadFile, File, Form
from typing import List
from app.conversores.pdf import procesar_pdf

enrutador_pdf = APIRouter()

@enrutador_pdf.post("/editar-pdf")
async def editar_pdf(
    archivos: List[UploadFile] = File(...),
    operacion: str = Form(...),
    opciones: str = Form("{}"),
):
    """Edita archivos PDF (unir, dividir, comprimir, rotar)."""
    lista_bytes = []
    for archivo in archivos:
        bytes_archivo = await archivo.read()
        lista_bytes.append(bytes_archivo)
        
    try:
        dict_opciones = json.loads(opciones)
    except Exception:
        dict_opciones = {}
        
    bytes_salida = procesar_pdf(lista_bytes, operacion, dict_opciones)
    
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

