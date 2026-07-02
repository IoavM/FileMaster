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

    TAMANO_MAXIMO_MB: int = 50
    TAMANO_MAXIMO_BYTES: int = 50 * 1024 * 1024

    # CORS
    ORIGENES_PERMITIDOS: list[str] = field(default_factory=lambda: [
        "http://localhost:5174",
        "http://localhost:5173",
        "http://localhost:3000",
        "https://file-master-chi.vercel.app",
        os.getenv("FRONTEND_URL", ""),
    ])

    ENTORNO: str = os.getenv("RENDER", "desarrollo")
    PUERTO: int = int(os.getenv("PORT", "8000"))

    def __post_init__(self):
        import tempfile
        base_temp = tempfile.gettempdir()
        self.DIR_TEMP = os.path.join(base_temp, "filemaster_temp")
        self.DIR_UPLOADS = os.path.join(base_temp, "filemaster_uploads")
        self.DIR_OUTPUTS = os.path.join(base_temp, "filemaster_outputs")

        self.ORIGENES_PERMITIDOS = [o for o in self.ORIGENES_PERMITIDOS if o]

configuracion = Configuracion()
