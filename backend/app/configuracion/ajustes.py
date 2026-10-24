"""
Configuración centralizada del backend.
Variables de entorno y constantes del proyecto.
"""
import os
from dataclasses import dataclass, field

@dataclass
class Configuracion:
    """Configuración del servidor."""

    DIR_BASE: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DIR_TEMP: str = field(default="")
    DIR_UPLOADS: str = field(default="")
    DIR_OUTPUTS: str = field(default="")

    TAMANO_MAXIMO_MB: int = 1024
    TAMANO_MAXIMO_BYTES: int = 1024 * 1024 * 1024

    # CORS restrictivo defensivo
    ORIGENES_PERMITIDOS: list[str] = field(default_factory=lambda: [
        "http://localhost:5174",
        "http://localhost:5173",
        "http://localhost:3000",
        "https://file-master-chi.vercel.app",
    ])
    METODOS_CORS_PERMITIDOS: list[str] = field(default_factory=lambda: [
        "GET",
        "POST",
        "OPTIONS",
    ])
    CABECERAS_CORS_PERMITIDAS: list[str] = field(default_factory=lambda: [
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ])

    # Límites de tasa (Rate Limiting)
    TASA_LIMITE_GENERAL: int = 60  # Peticiones / minuto por IP
    TASA_LIMITE_SENSIBLE: int = 5  # Intentos / minuto por IP para contraseñas / desbloqueo

    ENTORNO: str = os.getenv("RENDER", "desarrollo")
    PUERTO: int = int(os.getenv("PORT", "8000"))

    def __post_init__(self):
        import tempfile
        base_temp = tempfile.gettempdir()
        self.DIR_TEMP = os.path.join(base_temp, "filemaster_temp")
        self.DIR_UPLOADS = os.path.join(base_temp, "filemaster_uploads")
        self.DIR_OUTPUTS = os.path.join(base_temp, "filemaster_outputs")

        frontend_url = os.getenv("FRONTEND_URL", "").strip()
        if frontend_url and frontend_url not in self.ORIGENES_PERMITIDOS:
            self.ORIGENES_PERMITIDOS.append(frontend_url)

        self.ORIGENES_PERMITIDOS = [o for o in self.ORIGENES_PERMITIDOS if o]

configuracion = Configuracion()
