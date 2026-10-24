"""
Módulo de utilidades de seguridad defensiva para FileMaster (OWASP Top 10).
Incluye:
- Mitigación de fuerza bruta mediante limitación de tasa (Rate Limiting en memoria).
- Validación robusta de políticas de contraseñas.
- Comparación en tiempo constante y mitigación de timing attacks.
"""
import time
import secrets
import threading
from typing import Dict, List, Tuple


class LimitadorTasa:
    """
    Limitador de tasa en memoria por IP y endpoint con ventana deslizante.
    Seguro para entornos concurrentes mediante bloqueo de hilos (threading.Lock).
    """

    def __init__(self):
        self._registro: Dict[str, List[float]] = {}
        self._bloqueo = threading.Lock()
        self._ultimo_barrido = time.monotonic()

    def _limpiar_antiguos(self, ventana_segundos: float = 60.0):
        """Elimina registros que hayan superado la ventana temporal para liberar memoria."""
        ahora = time.monotonic()
        # Realizar barrido solo cada 30 segundos
        if ahora - self._ultimo_barrido < 30.0:
            return
        self._ultimo_barrido = ahora
        claves_eliminar = []
        for clave, marcas in list(self._registro.items()):
            filtradas = [m for m in marcas if ahora - m < ventana_segundos]
            if filtradas:
                self._registro[clave] = filtradas
            else:
                claves_eliminar.append(clave)
        for clave in claves_eliminar:
            self._registro.pop(clave, None)

    def verificar_limite(
        self,
        identificador: str,
        operacion: str = "general",
        max_peticiones: int = 60,
        ventana_segundos: float = 60.0,
    ) -> Tuple[bool, int]:
        """
        Verifica si la petición del identificador supera el límite configurado.
        Retorna: (permitido: bool, reintentar_en_segundos: int)
        """
        ahora = time.monotonic()
        clave = f"{identificador}:{operacion}"

        with self._bloqueo:
            self._limpiar_antiguos(ventana_segundos)
            marcas = self._registro.get(clave, [])
            marcas = [m for m in marcas if ahora - m < ventana_segundos]

            if len(marcas) >= max_peticiones:
                tiempo_mas_antiguo = marcas[0]
                tiempo_restante = max(1, int(ventana_segundos - (ahora - tiempo_mas_antiguo)))
                self._registro[clave] = marcas
                return False, tiempo_restante

            marcas.append(ahora)
            self._registro[clave] = marcas
            return True, 0


# Instancia singleton del limitador de tasa
limitador_tasa = LimitadorTasa()


def validar_fuerza_contrasena(clave: str) -> Tuple[bool, str]:
    """
    Valida la robustez de una contraseña siguiendo recomendaciones de OWASP (A07).
    Requisitos:
    - Longitud entre 8 y 128 caracteres.
    - No puede componerse únicamente de espacios.
    - Debe contener letras y al menos un número o símbolo.
    """
    if not clave or not clave.strip():
        return False, "La contraseña no puede estar vacía ni contener solo espacios."

    if len(clave) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres para garantizar su seguridad."

    if len(clave) > 128:
        return False, "La contraseña excede el límite máximo seguro de 128 caracteres."

    tiene_letra = any(c.isalpha() for c in clave)
    tiene_numero_o_simbolo = any(not c.isalpha() and not c.isspace() for c in clave)

    if not (tiene_letra and tiene_numero_o_simbolo):
        return False, "La contraseña debe combinar letras con al menos un número o símbolo especial."

    return True, ""


def comparar_en_tiempo_constante(val1: str, val2: str) -> bool:
    """
    Compara dos cadenas en tiempo constante para neutralizar ataques de tiempo (Timing Attacks).
    """
    return secrets.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))


def mitigar_ataque_tiempo(tiempo_inicio: float, tiempo_minimo: float = 0.35) -> None:
    """
    Garantiza que la respuesta no se devuelva antes de un umbral temporal mínimo,
    evitando que un atacante determine la validez parcial o longitud de una clave por diferencias en microsegundos.
    """
    transcurrido = time.monotonic() - tiempo_inicio
    diferencia = tiempo_minimo - transcurrido
    if diferencia > 0:
        time.sleep(diferencia)
