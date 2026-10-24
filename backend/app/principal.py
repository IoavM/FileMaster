"""
FileMaster Backend — FastAPI
Servidor principal de la API para conversión de archivos y herramientas.
Blindado con defensas OWASP Top 10 (Rate limiting, CORS restrictivo, cabeceras defensivas y sanitización de errores 500).
Optimizado con middlewares ASGI puros para evitar deadlocks de streaming en subida de archivos (UploadFile).
"""
import os
import sys
import logging
from contextlib import asynccontextmanager

# Asegurar resolución de importaciones de la aplicación en sys.path
_dir_backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir_backend not in sys.path:
    sys.path.insert(0, _dir_backend)

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Scope, Receive, Send

try:
    from app.configuracion.ajustes import configuracion
    from app.utilidades.seguridad import limitador_tasa
    from app.api.rutas_conversion import enrutador_conversion
    from app.api.rutas_pdf import enrutador_pdf
    from app.api.rutas_qr import enrutador_qr
    from app.api.rutas_tts import enrutador_tts
    from app.api.rutas_compresor import enrutador_compresor
    from app.api.rutas_detector_ia import enrutador_detector_ia
except (ImportError, ModuleNotFoundError):
    from configuracion.ajustes import configuracion
    from utilidades.seguridad import limitador_tasa
    from api.rutas_conversion import enrutador_conversion
    from api.rutas_pdf import enrutador_pdf
    from api.rutas_qr import enrutador_qr
    from api.rutas_tts import enrutador_tts
    from api.rutas_compresor import enrutador_compresor
    from api.rutas_detector_ia import enrutador_detector_ia

# Configuración de registro estructurado y seguro
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("filemaster.api")


@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    """Limpieza y creación de directorios temporales seguros al iniciar y cerrar."""
    os.makedirs(configuracion.DIR_TEMP, exist_ok=True)
    os.makedirs(configuracion.DIR_UPLOADS, exist_ok=True)
    os.makedirs(configuracion.DIR_OUTPUTS, exist_ok=True)
    yield


app = FastAPI(
    title="FileMaster API",
    description="API defensiva y gratuita para conversión de archivos y herramientas multimedia.",
    version="1.0.1",
    lifespan=ciclo_vida,
)


class CabecerasSeguridadMiddleware:
    """
    Middleware defensivo puro ASGI para inyectar cabeceras de seguridad HTTP (OWASP A05).
    No clona ni bloquea el stream de datos multipart/form-data.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_con_cabeceras(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["X-XSS-Protection"] = "1; mode=block"
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
                headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "img-src 'self' data: blob:; "
                    "font-src 'self' https://fonts.gstatic.com; "
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                    "connect-src 'self' https:;"
                )
                if "server" in headers:
                    del headers["server"]
            await send(message)

        await self.app(scope, receive, send_con_cabeceras)


class LimitadorTasaMiddleware:
    """
    Middleware defensivo puro ASGI para mitigación de fuerza bruta y DoS (OWASP A04).
    Lee únicamente los headers de scope sin consumir ni alterar el stream de recepción de archivos.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "")

        # Excluir comprobación de salud y preflight OPTIONS
        if path == "/api/salud" or method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        # Extraer IP cliente desde los metadatos de la conexión ASGI
        raw_headers = dict(scope.get("headers", []))
        x_forwarded_for = raw_headers.get(b"x-forwarded-for")
        if x_forwarded_for:
            ip = x_forwarded_for.decode("latin1").split(",")[0].strip()
        else:
            client = scope.get("client")
            ip = client[0] if client else "127.0.0.1"

        permitido, reintentar_en = limitador_tasa.verificar_limite(
            identificador=ip,
            operacion="api_general",
            max_peticiones=configuracion.TASA_LIMITE_GENERAL,
            ventana_segundos=60.0,
        )

        if not permitido:
            logger.warning(f"Límite de tasa excedido para IP: {ip} en {path}")
            response = JSONResponse(
                status_code=429,
                content={
                    "detalle": "Demasiadas solicitudes. Límite de tasa excedido. Por favor intenta más tarde."
                },
                headers={"Retry-After": str(reintentar_en)},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


# Registro de middlewares en orden de procesamiento (ASGI)
app.add_middleware(CabecerasSeguridadMiddleware)
app.add_middleware(LimitadorTasaMiddleware)

# CORS defensivo: permite localhost y cualquier subdominio vercel.app
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.ORIGENES_PERMITIDOS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)


# ==============================================================================
# MANEJADORES GLOBALES DE EXCEPCIONES: SANITIZACIÓN 500 (OWASP A05)
# ==============================================================================
@app.exception_handler(HTTPException)
async def manejador_http_exception(request: Request, exc: HTTPException):
    """Sanitiza excepciones HTTP 500 o superiores para no filtrar trazas ni rutas internas."""
    if exc.status_code >= 500:
        logger.error(
            f"Error interno HTTP 500 en [{request.method}] {request.url.path}: {exc.detail}",
            exc_info=True
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detalle": "Ocurrió un error interno en el servidor al procesar su solicitud. Por favor intente más tarde."
            }
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detalle": exc.detail}
    )


@app.exception_handler(Exception)
async def manejador_excepciones_no_controladas(request: Request, exc: Exception):
    """Captura cualquier excepción no manejada, la registra con trazabilidad y responde con error sanitizado."""
    logger.critical(
        f"Excepción crítica no controlada en [{request.method}] {request.url.path}: {exc}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "detalle": "Ocurrió un error interno en el servidor. Por favor verifique el formato de los datos o intente más tarde."
        }
    )


# Registrar rutas de la API
app.include_router(enrutador_conversion, prefix="/api", tags=["Conversión"])
app.include_router(enrutador_pdf, prefix="/api", tags=["PDF"])
app.include_router(enrutador_qr, prefix="/api", tags=["QR"])
app.include_router(enrutador_tts, prefix="/api", tags=["Texto a Voz"])
app.include_router(enrutador_compresor, prefix="/api", tags=["Compresor"])
app.include_router(enrutador_detector_ia, prefix="/api", tags=["Detector y Humanizador IA"])


@app.get("/api/salud")
async def verificar_salud():
    """Endpoint de verificación de salud del servidor."""
    return {"estado": "activo", "version": "1.0.1"}
