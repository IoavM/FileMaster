"""
Rutas de la API para Detección y Humanización de Texto IA.
Con sanitización de errores defensiva (OWASP A05).
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.servicios.detector_ia import (
    analizar_texto_ia,
    humanizar_texto,
    extraer_perfil_estilo
)

logger = logging.getLogger("filemaster.detector_ia")
enrutador_detector_ia = APIRouter(prefix="/detector-ia", tags=["Detector y Humanizador IA"])


class SolicitudAnalisis(BaseModel):
    texto: str = Field(..., min_length=10, description="Texto a analizar para detectar probabilidad de IA")


class SolicitudHumanizacion(BaseModel):
    texto: str = Field(..., min_length=10, description="Texto a humanizar")
    modo: str = Field("automatico", description="Modo: 'automatico' o 'estilo_personal'")
    nivel: str = Field("equilibrado", description="Nivel para modo automático: 'casual', 'equilibrado', 'academico'")
    texto_muestra_usuario: Optional[str] = Field("", description="Muestra de texto escrita por el usuario para imitar su estilo")


class SolicitudPerfilEstilo(BaseModel):
    texto_muestra: str = Field(..., min_length=15, description="Texto de muestra escrito por el usuario")


@enrutador_detector_ia.post("/analizar")
async def endpoint_analizar_texto(solicitud: SolicitudAnalisis):
    """Analiza un texto y devuelve el porcentaje de probabilidad de IA, métricas y desglose por oraciones."""
    try:
        resultado = analizar_texto_ia(solicitud.texto)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error procesando análisis de IA: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al procesar el análisis de texto.")


@enrutador_detector_ia.post("/humanizar")
async def endpoint_humanizar_texto(solicitud: SolicitudHumanizacion):
    """Humaniza un texto en modo automático o adaptándolo al estilo del usuario."""
    try:
        resultado = humanizar_texto(
            texto=solicitud.texto,
            modo=solicitud.modo,
            nivel=solicitud.nivel,
            texto_muestra_usuario=solicitud.texto_muestra_usuario or ""
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error procesando humanización de texto: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al humanizar el texto.")


@enrutador_detector_ia.post("/analizar-estilo")
async def endpoint_analizar_estilo(solicitud: SolicitudPerfilEstilo):
    """Extrae el perfil estilométrico de una muestra escrita por el usuario."""
    try:
        resultado = extraer_perfil_estilo(solicitud.texto_muestra)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error extrayendo perfil estilométrico: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al analizar el estilo del usuario.")
