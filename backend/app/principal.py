"""
FileMaster Backend — FastAPI
Servidor principal de la API para conversión de archivos y herramientas.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuracion.ajustes import configuracion
from app.api.rutas_conversion import enrutador_conversion
from app.api.rutas_pdf import enrutador_pdf
from app.api.rutas_qr import enrutador_qr
from app.api.rutas_tts import enrutador_tts
from app.api.rutas_youtube import enrutador_youtube
from app.api.rutas_fondo import enrutador_fondo
from app.api.rutas_compresor import enrutador_compresor

@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    """Limpieza de archivos temporales al iniciar y cerrar."""
    # Crear directorios temporales
    os.makedirs(configuracion.DIR_TEMP, exist_ok=True)
    os.makedirs(configuracion.DIR_UPLOADS, exist_ok=True)
    os.makedirs(configuracion.DIR_OUTPUTS, exist_ok=True)
    yield

app = FastAPI(
    title="FileMaster API",
    description="API gratuita para conversión de archivos y herramientas multimedia.",
    version="1.0.0",
    lifespan=ciclo_vida,
)

# CORS — permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.ORIGENES_PERMITIDOS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(enrutador_conversion, prefix="/api", tags=["Conversión"])
app.include_router(enrutador_pdf, prefix="/api", tags=["PDF"])
app.include_router(enrutador_qr, prefix="/api", tags=["QR"])
app.include_router(enrutador_tts, prefix="/api", tags=["Texto a Voz"])
app.include_router(enrutador_youtube, prefix="/api", tags=["YouTube"])
app.include_router(enrutador_fondo, prefix="/api", tags=["Eliminar Fondo"])
app.include_router(enrutador_compresor, prefix="/api", tags=["Compresor"])

@app.get("/api/salud")
async def verificar_salud():
    """Endpoint de verificación de salud del servidor."""
    return {"estado": "activo", "version": "1.0.0"}
