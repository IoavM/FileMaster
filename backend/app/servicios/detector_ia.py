"""
Servicio de Detección y Humanización de Texto IA.
Analiza la probabilidad de autoría por IA mediante métricas de Burstiness,
predictibilidad léxica, perplejidad y detección de clichés sintácticos.
Permite humanizar textos en modo automático o adaptándolos al estilo propio del usuario.
"""
import re
import math
import random
import statistics

# ==============================================================================
# CATÁLOGO DE CLICHÉS Y MARCADORES DISCURSIVOS DE IA (ESPAÑOL E INGLÉS)
# ==============================================================================

CLICHES_IA_ES = [
    # Transiciones formulaicas típicas de ChatGPT / Claude / Gemini
    r"\ben conclusión\b,?",
    r"\ben resumen\b,?",
    r"\ba modo de conclusión\b,?",
    r"\bpara concluir\b,?",
    r"\ben síntesis\b,?",
    r"\bcabe destacar que\b",
    r"\bes importante destacar que\b",
    r"\bes importante señalar que\b",
    r"\bvale la pena mencionar que\b",
    r"\bes menester (mencionar|indicar|resaltar)\b",
    r"\bno se puede subestimar\b",
    r"\bpor ende\b,?",
    r"\basimismo\b,?",
    r"\bpor consiguiente\b,?",
    r"\ba fin de cuentas\b,?",
    r"\ben última instancia\b,?",
    
    # Metáforas y fórmulas de relleno
    r"\bjuega un papel (crucial|fundamental|clave)\b",
    r"\bdesempeña un papel (crucial|fundamental|clave)\b",
    r"\bun tapiz de\b",
    r"\ben el vertiginoso mundo\b",
    r"\bun testimonio de\b",
    r"\bun faro de\b",
    r"\bmarcar un antes y un después\b",
    r"\bsin lugar a dudas\b,?",
    r"\ba través del prisma de\b",
    r"\bforjando el camino\b",
    r"\ben constante evolución\b",
    r"\bun abanico de posibilidades\b",
    r"\bno solo ([^,]+) sino también\b",
    r"\bno solo ([^,]+) sino que además\b",
    r"\bes crucial (comprender|entender|analizar|considerar)\b",
    r"\bresulta fundamental\b",
    r"\bde vital importancia\b",
    r"\bun equilibrio delicado\b",
    r"\bun recordatorio de\b",
    r"\babre nuevas fronteras\b",
    r"\bcomo se mencionó anteriormente\b",
    r"\ben el panorama actual\b",
    r"\bpermite vislumbrar\b"
]

CLICHES_IA_EN = [
    r"\bin conclusion\b,?",
    r"\bto sum up\b,?",
    r"\bit is important to note that\b",
    r"\bit is worth noting that\b",
    r"\bplays a crucial role\b",
    r"\bplays a pivotal role\b",
    r"\ba tapestry of\b",
    r"\ba testament to\b",
    r"\bin today's fast-paced world\b",
    r"\bnavigating the complexities of\b",
    r"\bdelve into\b",
    r"\ba myriad of\b",
    r"\bever-evolving\b",
    r"\bfosters\b",
    r"\bunderscores\b",
    r"\bbeacon of\b",
    r"\bnot only ([^,]+) but also\b",
    r"\bit is crucial to\b",
    r"\bultimately\b,?",
    r"\bin the modern era\b"
]

# Sustitutos naturales para la humanización (100% de cobertura de clichés)
REEMPLAZOS_CLICHES_ES = [
    (r"\ben el vertiginoso mundo actual\b,?", ["hoy en día,", "con el ritmo actual,", "en estos tiempos,"]),
    (r"\ben el vertiginoso mundo de\b", ["en el día a día de", "dentro de"]),
    (r"\bjuega un papel (crucial|fundamental|clave)\b", ["es esencial", "marca la diferencia", "resulta decisivo", "tiene un gran impacto"]),
    (r"\bdesempeña un papel (crucial|fundamental|clave)\b", ["es vital", "influye directamente", "marca la pauta"]),
    (r"\bes importante destacar que\b", ["conviene notar que", "llama la atención que", "la clave está en que", "hay que ver que"]),
    (r"\bes importante señalar que\b", ["vale recalcar que", "un punto a considerar es que", "ojo con que"]),
    (r"\bvale la pena mencionar que\b", ["un detalle interesante es que", "también cuenta que", "vale la pena ver que"]),
    (r"\bcabe destacar que\b", ["un punto clave es que", "hay que resaltar que", "lo notable es que"]),
    (r"\bcabe señalar que\b", ["vale aclarar que", "no hay que olvidar que", "un dato relevante:"]),
    (r"\bes menester (mencionar|indicar|resaltar)\b", ["conviene apuntar", "hace falta decir", "vale decir"]),
    (r"\bno se puede subestimar\b", ["no hay que perder de vista", "pesa bastante"]),
    (r"\bun testimonio de\b", ["una muestra de", "una clara prueba de"]),
    (r"\bun faro de\b", ["una referencia en", "una guía para"]),
    (r"\bmarcar un antes y un después\b", ["cambiar las reglas del juego", "dar un giro total"]),
    (r"\ba través del prisma de\b", ["desde el punto de vista de", "mirándolo desde"]),
    (r"\ben constante evolución\b", ["cambiando a diario", "en pleno cambio", "siempre en movimiento"]),
    (r"\bes crucial (comprender|entender|analizar|considerar)\b", ["hace falta entender", "es clave mirar", "conviene revisar"]),
    (r"\bun equilibrio delicado\b", ["un balance fino", "un punto medio"]),
    (r"\bun recordatorio de\b", ["una señal de", "un aviso claro de"]),
    (r"\babre nuevas fronteras\b", ["abre nuevas puertas", "ofrece más caminos"]),
    (r"\bcomo se mencionó anteriormente\b", ["como decía antes", "tal como vimos"]),
    (r"\bpermite vislumbrar\b", ["deja ver", "muestra", "anuncia"]),
    (r"\bun tapiz de\b", ["una combinación de", "un conjunto de", "una mezcla de"]),
    (r"\bun abanico de posibilidades\b", ["muchas opciones", "distintas alternativas", "varios caminos"]),
    (r"\bforjando el camino\b", ["abriendo paso", "marcando el rumbo", "dando pie"]),
    (r"\bresulta fundamental\b", ["es indispensable", "hace falta", "conviene"]),
    (r"\bde vital importancia\b", ["muy valioso", "prioritario", "clave"]),
    (r"\ben conclusión\b,?", ["al final del día,", "en pocas palabras,", "en definitiva,", "en el fondo,"]),
    (r"\ben resumen\b,?", ["en pocas palabras,", "en concreto,", "básicamente,"]),
    (r"\ba modo de conclusión\b,?", ["para cerrar,", "al final,"]),
    (r"\bpara concluir\b,?", ["para terminar,", "por último,"]),
    (r"\ben síntesis\b,?", ["en resumen breve,", "en pocas palabras,"]),
    (r"\bpor consiguiente\b,?", ["por eso,", "así que,", "de ahí que"]),
    (r"\basimismo\b,?", ["de hecho,", "además,", "por otro lado,"]),
    (r"\bpor ende\b,?", ["por tanto,", "por eso mismo,"]),
    (r"\bsin lugar a dudas\b,?", ["claramente,", "sin duda,", "desde luego,"]),
    (r"\ba fin de cuentas\b,?", ["al fin y al cabo,", "mirándolo bien,"]),
    (r"\ben última instancia\b,?", ["al fin y al cabo,", "en el fondo,"]),
    (r"\ben el panorama actual\b,?", ["hoy por hoy,", "actualmente,"]),
    (r"\bno solo ([^,]+) sino también\b", r"tanto \1 como"),
    (r"\bno solo ([^,]+) sino que además\b", r"tanto \1 como"),
]

REEMPLAZOS_CLICHES_EN = [
    (r"\bin conclusion\b,?", ["all in all,", "in short,", "at the end of the day,"]),
    (r"\bto sum up\b,?", ["to wrap up,", "in short,"]),
    (r"\bit is important to note that\b", ["it's worth noting that", "keep in mind that", "notably,"]),
    (r"\bit is worth noting that\b", ["notably,", "interestingly,", "keep in mind,"]),
    (r"\bplays a (crucial|pivotal|key) role\b", ["is key", "makes a big difference", "matters deeply"]),
    (r"\ba tapestry of\b", ["a rich mix of", "a wide variety of"]),
    (r"\ba testament to\b", ["a clear sign of", "solid proof of"]),
    (r"\ba myriad of\b", ["plenty of", "many", "various"]),
    (r"\bdelve into\b", ["explore", "look into", "examine"]),
    (r"\bin today's fast-paced world\b,?", ["nowadays,", "today,", "in modern times,"]),
    (r"\bnavigating the complexities of\b", ["dealing with", "tackling", "managing"]),
    (r"\bever-evolving\b", ["changing", "dynamic", "fast-moving"]),
    (r"\bfosters\b", ["encourages", "drives", "helps build"]),
    (r"\bunderscores\b", ["highlights", "shows", "stresses"]),
    (r"\bbeacon of\b", ["guide for", "model of"]),
    (r"\bnot only ([^,]+) but also\b", r"both \1 and"),
    (r"\bit is crucial to\b", ["it's essential to", "you need to"]),
    (r"\bultimately\b,?", ["in the end,", "when all is said and done,"]),
    (r"\bin the modern era\b,?", ["today,", "nowadays,"]),
]

_PASIVAS_EXTENDIDAS_ES = [
    (r"\bes considerada\b", ["se toma como", "funciona como", "suele verse como"]),
    (r"\bson consideradas\b", ["se toman como", "funcionan como"]),
    (r"\bresulta esencial\b", ["hace mucha falta", "es clave", "conviene"]),
    (r"\bresulta evidente\b", ["queda claro", "salta a la vista"]),
    (r"\brepresenta un\b", ["supone un", "es un"]),
    (r"\brepresentan un\b", ["suponen un", "son un"]),
    (r"\bdependen de\b", ["están atadas a", "van de la mano con"]),
    (r"\bse traduce en\b", ["termina en", "lleva a"]),
]

_PASIVAS_EXTENDIDAS_EN = [
    (r"\bis considered\b", ["is seen as", "works as", "acts as"]),
    (r"\bare considered\b", ["are seen as", "work as"]),
    (r"\bproves essential\b", ["is key", "is crucial"]),
    (r"\brepresents a\b", ["is a", "serves as a"]),
    (r"\bare dependent on\b", ["rely on", "go hand in hand with"]),
]

_PUNCH_LINES_ES = [
    "Y funciona.",
    "El motivo es simple.",
    "No es casualidad.",
    "La diferencia se nota.",
    "Tiene todo el sentido.",
    "Los datos lo avalan.",
    "Así de claro.",
]

_PUNCH_LINES_EN = [
    "And it works.",
    "The reason is simple.",
    "It's no coincidence.",
    "The difference is clear.",
    "That makes total sense.",
    "The numbers back this up.",
    "Simple as that."
]



# ==============================================================================
# FUNCIONES AUXILIARES DE ANÁLISIS
# ==============================================================================

def dividir_en_oraciones(texto: str) -> list[str]:
    """Divide el texto en oraciones respetando la puntuación final."""
    partes = re.split(r'(?<=[.!?])\s+', texto.strip())
    oraciones = [p.strip() for p in partes if p.strip() and len(p.strip()) > 3]
    return oraciones


def calcular_burstiness(longitudes: list[int]) -> tuple[float, float, float]:
    """
    Calcula la longitud media, la desviación estándar y el score de burstiness (0-100).
    Umbrales recalibrados para ser mucho más sensibles a la uniformidad de IA.
    """
    if not longitudes:
        return 0.0, 0.0, 50.0
    media = statistics.mean(longitudes)
    if len(longitudes) < 2:
        return media, 0.0, 50.0
    desv = statistics.stdev(longitudes)

    cv = desv / max(1.0, media)

    # Escala continua en lugar de saltos discretos
    # IA: CV típico 0.15-0.30, σ 2-5
    # Humano: CV típico 0.45-0.80, σ 8-15+
    if cv < 0.18:
        score = 96.0
    elif cv < 0.25:
        score = 88.0
    elif cv < 0.32:
        score = 75.0
    elif cv < 0.40:
        score = 60.0
    elif cv < 0.50:
        score = 42.0
    elif cv < 0.60:
        score = 25.0
    elif cv < 0.75:
        score = 12.0
    else:
        score = 4.0

    # Bonus: si la σ absoluta es muy baja, reforzar
    if desv < 2.5:
        score = max(score, 94.0)
    elif desv < 4.0:
        score = max(score, 82.0)

    return round(media, 1), round(desv, 1), score


def calcular_riqueza_lexica(texto: str) -> tuple[float, float]:
    """
    Type-Token Ratio. El TTR alto NO debe despenalizar el score,
    ya que la IA moderna también produce TTR alto en textos cortos.
    """
    palabras = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+\b', texto.lower())
    total_tokens = len(palabras)
    if not total_tokens:
        return 0.0, 50.0
    tokens_unicos = len(set(palabras))
    ttr = tokens_unicos / total_tokens

    if total_tokens > 60:
        # IA: TTR típico 0.40-0.62 para textos largos
        if 0.42 <= ttr <= 0.58:
            score = 78.0
        elif 0.38 <= ttr < 0.42 or 0.58 < ttr <= 0.65:
            score = 60.0
        elif ttr < 0.38:
            score = 72.0  # Muy repetitivo, sospechoso
        else:
            score = 40.0  # TTR alto: neutral, no exonera
    elif total_tokens > 30:
        if 0.48 <= ttr <= 0.68:
            score = 65.0
        elif ttr > 0.68:
            score = 42.0  # Neutral
        else:
            score = 55.0
    else:
        score = 45.0

    return round(ttr * 100, 1), score


# ---- Conectores y transiciones amplios (no solo clichés, sino todo conector formal) ----
_TRANSICIONES_ES = [
    r"\bademás\b", r"\basimismo\b", r"\bpor otro lado\b", r"\bpor otra parte\b",
    r"\ben primer lugar\b", r"\ben segundo lugar\b", r"\bpor ende\b",
    r"\bpor consiguiente\b", r"\ben consecuencia\b", r"\bpor lo tanto\b",
    r"\bno obstante\b", r"\bsin embargo\b", r"\bde igual manera\b",
    r"\bde igual forma\b", r"\ben este sentido\b", r"\bdicho lo anterior\b",
    r"\bcabe destacar\b", r"\bcabe señalar\b", r"\bcabe mencionar\b",
    r"\bes importante\b", r"\bes necesario\b", r"\bes fundamental\b",
    r"\bes crucial\b", r"\bes preciso\b", r"\bes evidente\b",
    r"\bde esta manera\b", r"\bde este modo\b", r"\bfinalmente\b",
    r"\ben definitiva\b", r"\ben conclusión\b", r"\ben resumen\b",
    r"\bcon respecto a\b", r"\ben relación con\b", r"\ba su vez\b",
    r"\ben efecto\b", r"\bde hecho\b", r"\bpor el contrario\b",
    r"\bpor tanto\b", r"\basi pues\b", r"\ben particular\b",
]
_TRANSICIONES_EN = [
    r"\bfurthermore\b", r"\bmoreover\b", r"\badditionally\b", r"\bconsequently\b",
    r"\btherefore\b", r"\bnevertheless\b", r"\bnonetheless\b", r"\bhowever\b",
    r"\bin addition\b", r"\bin contrast\b", r"\bon the other hand\b",
    r"\bspecifically\b", r"\bultimately\b", r"\bfundamentally\b",
    r"\bit is important\b", r"\bit is worth\b", r"\bit is essential\b",
    r"\bit is crucial\b", r"\bin particular\b", r"\bin fact\b",
    r"\bas a result\b", r"\bfor instance\b", r"\bfor example\b",
    r"\bin summary\b", r"\bin conclusion\b", r"\bto summarize\b",
    r"\bfirstly\b", r"\bsecondly\b", r"\bthirdly\b", r"\blastly\b",
]


def _calcular_diversidad_inicios(oraciones: list[str]) -> float:
    """
    Mide qué tan variados son los inicios de las oraciones (primeras 2-3 palabras).
    La IA tiende a empezar muchas oraciones con patrones similares.
    Score alto = más probable IA (poca diversidad).
    """
    if len(oraciones) < 3:
        return 50.0

    inicios = []
    for o in oraciones:
        words = o.split()
        if len(words) >= 2:
            inicios.append(words[0].lower())

    if not inicios:
        return 50.0

    total = len(inicios)
    unicos = len(set(inicios))
    ratio_diversidad = unicos / total

    # Patrones de inicio robóticos comunes
    patrones_ia = [
        r"^(el|la|los|las|un|una|este|esta|estos|estas)\b",
        r"^(it|this|the|these|that|there|they|we|one)\b",
        r"^(en|con|por|para|de|a)\b",
        r"^(además|asimismo|igualmente|también|furthermore|moreover|additionally)\b",
    ]
    cuenta_patron = 0
    for o in oraciones:
        for pat in patrones_ia:
            if re.match(pat, o.strip(), flags=re.IGNORECASE):
                cuenta_patron += 1
                break

    ratio_patron = cuenta_patron / max(1, total)

    # Score: baja diversidad + muchos patrones repetidos = IA
    if ratio_diversidad < 0.35:
        score = 92.0
    elif ratio_diversidad < 0.50:
        score = 75.0
    elif ratio_diversidad < 0.65:
        score = 55.0
    elif ratio_diversidad < 0.80:
        score = 30.0
    else:
        score = 10.0

    # Bonus si muchas oraciones empiezan con artículos/pronombres predecibles
    if ratio_patron > 0.75:
        score = min(98, score + 15)
    elif ratio_patron > 0.60:
        score = min(98, score + 8)

    return score


def _calcular_densidad_transiciones(texto: str, total_palabras: int) -> float:
    """
    Mide la densidad de conectores formales y palabras de transición.
    La IA usa significativamente más transiciones que los humanos.
    """
    if total_palabras < 20:
        return 40.0

    total_trans = 0
    for pat in _TRANSICIONES_ES + _TRANSICIONES_EN:
        total_trans += len(re.findall(pat, texto, flags=re.IGNORECASE))

    densidad = (total_trans / total_palabras) * 100

    # Humano: ~0.5-1.5% de transiciones
    # IA: ~2-5% de transiciones (usa una en casi cada oración)
    if densidad > 4.0:
        return 96.0
    elif densidad > 3.0:
        return 88.0
    elif densidad > 2.2:
        return 76.0
    elif densidad > 1.5:
        return 60.0
    elif densidad > 1.0:
        return 42.0
    elif densidad > 0.5:
        return 22.0
    else:
        return 8.0


def _calcular_uniformidad_longitud_palabras(oraciones: list[str]) -> float:
    """
    Mide la uniformidad de la longitud promedio de palabras entre oraciones.
    La IA mantiene una complejidad léxica muy consistente oración a oración.
    Los humanos varían más (mezclan vocabulario simple con técnico).
    """
    if len(oraciones) < 3:
        return 45.0

    promedios = []
    for o in oraciones:
        palabras = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+\b', o)
        if len(palabras) >= 3:
            avg = statistics.mean(len(p) for p in palabras)
            promedios.append(avg)

    if len(promedios) < 3:
        return 45.0

    desv_promedios = statistics.stdev(promedios)

    # IA: σ del promedio de longitud de palabras entre oraciones ≈ 0.3-0.8
    # Humano: σ ≈ 1.0-2.5+
    if desv_promedios < 0.4:
        return 94.0
    elif desv_promedios < 0.6:
        return 82.0
    elif desv_promedios < 0.8:
        return 68.0
    elif desv_promedios < 1.0:
        return 50.0
    elif desv_promedios < 1.3:
        return 32.0
    elif desv_promedios < 1.8:
        return 18.0
    else:
        return 6.0


def _calcular_voz_pasiva(texto: str, total_oraciones: int) -> float:
    """
    Detecta el uso excesivo de voz pasiva, impersonal y construcciones
    despersonalizadas típicas de IA (patrones ampliados).
    """
    if total_oraciones < 2:
        return 40.0

    pasivas_es = [
        r"\bse ha\b", r"\bse han\b", r"\bse puede\b", r"\bse pueden\b",
        r"\bse debe\b", r"\bse deben\b", r"\bse observa\b", r"\bse nota\b",
        r"\bse evidencia\b", r"\bse considera\b", r"\bse requiere\b",
        r"\bse recomienda\b", r"\bse sugiere\b", r"\bse establece\b",
        r"\bse estima\b", r"\bse plantea\b", r"\bse destaca\b",
        r"\bse demuestra\b", r"\bse identifica\b", r"\bse determina\b",
        r"\bha sido\b", r"\bhan sido\b", r"\bfue demostrado\b",
        r"\bes posible\b", r"\bresulta\b", r"\bcabe\b",
        # Ampliados: formas despersonalizadas comunes de IA
        r"\bes considerada?\b", r"\bes una\b", r"\brepresenta\b",
        r"\brequiere\b", r"\bpermite\b", r"\bimplica\b",
        r"\bdependen? de\b", r"\bse ven?\b", r"\bconstituye\b",
        r"\bse encuentra\b", r"\bse presentan?\b",
        r"\bhan documentado\b", r"\bhan aumentado\b",
        r"\bes necesario\b", r"\bes fundamental\b", r"\bes esencial\b",
    ]
    pasivas_en = [
        r"\bit is\b", r"\bit has been\b", r"\bit can be\b", r"\bit should be\b",
        r"\bhas been\b", r"\bhave been\b", r"\bwas demonstrated\b",
        r"\bis considered\b", r"\bis observed\b", r"\bis suggested\b",
        r"\bcan be seen\b", r"\bcan be noted\b",
        r"\brepresents\b", r"\brequires\b", r"\ballows\b",
        r"\bis a\b", r"\bhave documented\b",
    ]

    total_pasivas = 0
    for pat in pasivas_es + pasivas_en:
        total_pasivas += len(re.findall(pat, texto, flags=re.IGNORECASE))

    ratio = total_pasivas / max(1, total_oraciones)

    # IA: ~0.6-2+ pasivas/impersonales por oración
    # Humano: ~0.1-0.3 por oración
    if ratio > 1.5:
        return 96.0
    elif ratio > 1.0:
        return 85.0
    elif ratio > 0.7:
        return 72.0
    elif ratio > 0.45:
        return 58.0
    elif ratio > 0.25:
        return 35.0
    else:
        return 10.0


# ==============================================================================
# MOTOR PRINCIPAL DE DETECCIÓN DE IA (v2 – Calibración agresiva)
# ==============================================================================

def analizar_texto_ia(texto: str) -> dict:
    """
    Analiza un texto y devuelve su porcentaje de probabilidad de IA,
    usando 6 métricas estadísticas ponderadas + detección de clichés.
    Calibración agresiva para competir con ZeroGPT/GPTZero.
    """
    if not texto or len(texto.strip()) < 30:
        return {
            "puntuacion_ia": 0,
            "etiqueta": "Texto muy corto",
            "color": "#64748B",
            "resumen": "Ingresa al menos 30 caracteres para obtener un análisis estadístico fiable.",
            "metricas": {
                "longitud_media_oraciones": 0,
                "desviacion_ritmo": 0,
                "total_palabras": len(texto.split()) if texto else 0,
                "cliches_detectados": 0,
                "riqueza_lexica_pct": 0,
            },
            "cliches": [],
            "oraciones": [],
        }

    oraciones = dividir_en_oraciones(texto)
    if not oraciones:
        return {
            "puntuacion_ia": 0,
            "etiqueta": "Sin oraciones",
            "color": "#64748B",
            "resumen": "No se detectaron oraciones completas.",
            "metricas": {"longitud_media_oraciones": 0, "desviacion_ritmo": 0, "total_palabras": 0, "cliches_detectados": 0, "riqueza_lexica_pct": 0},
            "cliches": [],
            "oraciones": [],
        }

    longitudes = [len(o.split()) for o in oraciones]
    total_palabras = sum(longitudes)

    # ── MÉTRICA 1: Burstiness (uniformidad de longitud de oraciones) ──
    media_long, desv_long, score_burstiness = calcular_burstiness(longitudes)

    # ── MÉTRICA 2: Clichés y marcadores robóticos ──
    cliches_totales = []
    lista_patrones = CLICHES_IA_ES + CLICHES_IA_EN
    for pat in lista_patrones:
        coincidencias = re.findall(pat, texto, flags=re.IGNORECASE)
        if coincidencias:
            nombre_limpio = pat.replace(r"\b", "").replace(",?", "").replace(r"\s+", " ")
            cliches_totales.extend([nombre_limpio] * len(coincidencias))

    densidad_cliches = (len(cliches_totales) / max(1, total_palabras)) * 100
    if densidad_cliches > 1.2:
        score_cliches = 96.0
    elif densidad_cliches > 0.7:
        score_cliches = 85.0
    elif densidad_cliches > 0.3:
        score_cliches = 65.0
    elif densidad_cliches > 0.1:
        score_cliches = 42.0
    elif densidad_cliches > 0.0:
        score_cliches = 25.0
    else:
        score_cliches = 8.0

    # ── MÉTRICA 3: Riqueza léxica (TTR) ──
    ttr_pct, score_ttr = calcular_riqueza_lexica(texto)

    # ── MÉTRICA 4: Diversidad de inicios de oraciones ──
    score_inicios = _calcular_diversidad_inicios(oraciones)

    # ── MÉTRICA 5: Densidad de transiciones formales ──
    score_transiciones = _calcular_densidad_transiciones(texto, total_palabras)

    # ── MÉTRICA 6: Uniformidad de longitud de palabras ──
    score_uniformidad = _calcular_uniformidad_longitud_palabras(oraciones)

    # ── MÉTRICA 7: Frecuencia de voz pasiva/impersonal ──
    score_pasiva = _calcular_voz_pasiva(texto, len(oraciones))

    # ── MÉTRICA 8: Compresión del rango de longitudes ──
    # Si TODAS las oraciones caen en un rango estrecho (ej: 10-15 palabras),
    # eso es extremadamente sospechoso de IA
    if len(longitudes) >= 4:
        rango = max(longitudes) - min(longitudes)
        if rango <= 3:
            score_rango = 96.0
        elif rango <= 5:
            score_rango = 82.0
        elif rango <= 8:
            score_rango = 60.0
        elif rango <= 12:
            score_rango = 35.0
        else:
            score_rango = 8.0
    else:
        score_rango = 50.0

    # ── PUNTUACIÓN GLOBAL PONDERADA (8 métricas) ──
    puntuacion_ia = round(
        (score_burstiness * 0.22) +       # Uniformidad de ritmo
        (score_rango * 0.13) +             # Compresión del rango
        (score_cliches * 0.12) +           # Clichés robóticos
        (score_ttr * 0.05) +               # Riqueza léxica
        (score_inicios * 0.13) +           # Diversidad de inicios
        (score_transiciones * 0.12) +      # Densidad de transiciones
        (score_uniformidad * 0.11) +       # Uniformidad de complejidad léxica
        (score_pasiva * 0.12)              # Voz pasiva/impersonal
    )

    # Aplicar curva de refuerzo: si varias métricas apuntan a IA, amplificar
    scores_individuales = [score_burstiness, score_rango, score_cliches, score_inicios,
                           score_transiciones, score_uniformidad, score_pasiva, score_ttr]
    altos = sum(1 for s in scores_individuales if s >= 60)
    if altos >= 6:
        puntuacion_ia = min(98, puntuacion_ia * 1.25)
    elif altos >= 5:
        puntuacion_ia = min(98, puntuacion_ia * 1.18)
    elif altos >= 4:
        puntuacion_ia = min(98, puntuacion_ia * 1.10)
    elif altos >= 3:
        puntuacion_ia = min(98, puntuacion_ia * 1.05)

    puntuacion_ia = round(max(2, min(98, puntuacion_ia)))

    # Calificación cualitativa
    if puntuacion_ia >= 72:
        etiqueta = "Altamente probable de IA"
        color = "#EF4444"
        resumen = "El texto muestra una cadencia sintáctica muy regular, transiciones formulaicas y patrones léxicos típicos de modelos de lenguaje."
    elif puntuacion_ia >= 48:
        etiqueta = "Sospecha moderada / Mixto"
        color = "#F59E0B"
        resumen = "El texto contiene una combinación de frases naturales con estructuras predecibles y algunas muletillas robóticas."
    elif puntuacion_ia >= 25:
        etiqueta = "Probablemente Humano"
        color = "#3B82F6"
        resumen = "La variación de longitud, vocabulario y naturalidad sugieren redacción humana con mínima o nula asistencia de IA."
    else:
        etiqueta = "100% Humano"
        color = "#10B981"
        resumen = "Excelente ritmo orgánico, rica variación y ausencia de patrones automatizados."

    # ── EVALUACIÓN INDIVIDUAL DE CADA ORACIÓN ──
    oraciones_analizadas = []
    for idx, o in enumerate(oraciones):
        o_words = len(o.split())
        cliches_en_o = []
        for pat in lista_patrones:
            if re.search(pat, o, flags=re.IGNORECASE):
                cliches_en_o.append(pat.replace(r"\b", "").replace(",?", ""))

        # Score base por longitud
        o_score = 20.0

        # Clichés
        if cliches_en_o:
            o_score += 35.0 * len(cliches_en_o)

        # Rango canónico de longitud monótona en IA (14 a 28 palabras)
        if 14 <= o_words <= 28:
            o_score += 20.0
        elif o_words < 6 or o_words > 35:
            o_score -= 20.0

        # Transiciones formales dentro de la oración
        trans_en_o = 0
        for pat in _TRANSICIONES_ES + _TRANSICIONES_EN:
            if re.search(pat, o, flags=re.IGNORECASE):
                trans_en_o += 1
        if trans_en_o >= 2:
            o_score += 25.0
        elif trans_en_o == 1:
            o_score += 12.0

        # Voz pasiva/impersonal en la oración
        pasivas_o = [r"\bse ha\b", r"\bse puede\b", r"\bse debe\b", r"\bse observa\b",
                     r"\bse considera\b", r"\bresulta\b", r"\bcabe\b", r"\bes posible\b",
                     r"\bit is\b", r"\bit has been\b", r"\bhas been\b"]
        for pat in pasivas_o:
            if re.search(pat, o, flags=re.IGNORECASE):
                o_score += 10.0
                break

        # Longitud de palabras muy uniforme dentro de la oración
        palabras_o = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+\b', o)
        if len(palabras_o) >= 5:
            avg_len = statistics.mean(len(p) for p in palabras_o)
            if 4.5 <= avg_len <= 6.5:
                o_score += 8.0  # Rango típico de IA

        o_score = max(3, min(99, round(o_score)))

        if o_score >= 60:
            nivel = "ia"
        elif o_score >= 35:
            nivel = "mixto"
        else:
            nivel = "humano"

        oraciones_analizadas.append({
            "id": idx,
            "texto": o,
            "puntuacion_ia": o_score,
            "nivel": nivel,
            "cliches": list(set(cliches_en_o)),
            "palabras": o_words,
        })

    return {
        "puntuacion_ia": puntuacion_ia,
        "etiqueta": etiqueta,
        "color": color,
        "resumen": resumen,
        "metricas": {
            "longitud_media_oraciones": media_long,
            "desviacion_ritmo": desv_long,
            "total_palabras": total_palabras,
            "cliches_detectados": len(cliches_totales),
            "riqueza_lexica_pct": ttr_pct,
        },
        "cliches": sorted(list(set(cliches_totales))),
        "oraciones": oraciones_analizadas,
    }


# ==============================================================================
# EXTRACCIÓN DE PERFIL ESTILOMÉTRICO DEL USUARIO
# ==============================================================================

def extraer_perfil_estilo(texto_muestra: str) -> dict:
    """
    Analiza un texto de muestra escrito por el usuario para extraer su perfil estilístico
    (longitud promedio de frases, persona gramatical, puntuación característica y tono).
    """
    if not texto_muestra or len(texto_muestra.strip()) < 25:
        return {
            "valido": False,
            "mensaje": "Ingresa una muestra de al menos 25 caracteres para extraer tus patrones de redacción.",
        }

    oraciones = dividir_en_oraciones(texto_muestra)
    longitudes = [len(o.split()) for o in oraciones]
    longitud_media = statistics.mean(longitudes) if longitudes else 12.0
    desv = statistics.stdev(longitudes) if len(longitudes) > 1 else 4.0

    txt_lower = texto_muestra.lower()

    # Persona gramatical
    cuenta_primera_sing = len(re.findall(r'\b(yo|mi|mis|me|estuve|hice|noté|creo|pienso|vi|probé|usé|siento|digo)\b', txt_lower))
    cuenta_primera_plur = len(re.findall(r'\b(nosotros|nos|hemos|hicimos|creemos|vemos|probamos|usamos|decimos)\b', txt_lower))

    if cuenta_primera_sing >= 2 and cuenta_primera_sing >= cuenta_primera_plur:
        persona = "1a_singular"
        tono_persona = "Primera persona (Yo)"
        icono_persona = "User"
    elif cuenta_primera_plur >= 2:
        persona = "1a_plural"
        tono_persona = "Primera persona colectiva (Nosotros)"
        icono_persona = "Users"
    else:
        persona = "impersonal"
        tono_persona = "Tercera persona / Impersonal"
        icono_persona = "FileText"

    # Puntuación característica
    usa_preguntas = "?" in texto_muestra or "¿" in texto_muestra
    usa_exclamaciones = "!" in texto_muestra or "¡" in texto_muestra
    usa_puntos_susp = "..." in texto_muestra or "…" in texto_muestra
    usa_guiones = "—" in texto_muestra or " - " in texto_muestra

    # Registro de formalidad
    palabras_coloquiales = len(re.findall(r'\b(la verdad|ojo|bueno|genial|súper|un par|bastante|totalmente|de plano|chulo|al tiro|dale|en fin)\b', txt_lower))
    if palabras_coloquiales >= 2 or longitud_media < 11:
        registro = "casual"
        etiqueta_registro = "Conversacional y dinámico"
    elif longitud_media > 22:
        registro = "academico"
        etiqueta_registro = "Formal y detallado"
    else:
        registro = "equilibrado"
        etiqueta_registro = "Claro y directo"

    # Conectores favoritos usados por el usuario
    conectores_candidatos = [
        "la verdad", "por eso", "de hecho", "además", "en cambio", "sin embargo",
        "por otro lado", "al final", "así que", "o sea", "es decir", "ojo"
    ]
    conectores_detectados = [c for c in conectores_candidatos if c in txt_lower]

    return {
        "valido": True,
        "longitud_media": round(longitud_media, 1),
        "desviacion": round(desv, 1),
        "persona": persona,
        "tono_persona": tono_persona,
        "icono_persona": icono_persona,
        "registro": registro,
        "etiqueta_registro": etiqueta_registro,
        "puntuacion": {
            "usa_preguntas": usa_preguntas,
            "usa_exclamaciones": usa_exclamaciones,
            "usa_puntos_suspensivos": usa_puntos_susp,
            "usa_guiones": usa_guiones,
        },
        "conectores_detectados": conectores_detectados,
        "resumen_estilo": f"{tono_persona} · {etiqueta_registro} · Frases de ~{round(longitud_media)} palabras",
    }


# ==============================================================================
# MOTOR DE HUMANIZACIÓN DE TEXTO (v2 – Reescritura profunda)
# ==============================================================================

# ---- Diccionario amplio de sinónimos formales → naturales (español) ----
_SINONIMOS_ES: list[tuple[str, list[str]]] = [
    # Verbos formales / robóticos
    (r"\butilizar\b", ["usar", "emplear", "recurrir a"]),
    (r"\bimplementar\b", ["aplicar", "poner en marcha", "usar"]),
    (r"\bproporcionar\b", ["dar", "ofrecer", "brindar"]),
    (r"\bfacilitar\b", ["hacer más fácil", "simplificar", "ayudar con"]),
    (r"\boptimizar\b", ["mejorar", "afinar", "ajustar"]),
    (r"\bgarantizar\b", ["asegurar", "confirmar"]),
    (r"\bposibilitar\b", ["permitir", "hacer posible", "abrir la puerta a"]),
    (r"\bcontribuir a\b", ["ayudar a", "sumar a", "aportar a"]),
    (r"\bgenerar\b", ["crear", "producir", "provocar"]),
    (r"\bfomentar\b", ["impulsar", "promover", "alimentar"]),
    (r"\babordar\b", ["tratar", "encarar", "atacar"]),
    (r"\bconllevar\b", ["implicar", "traer consigo", "suponer"]),
    (r"\bexhibir\b", ["mostrar", "presentar"]),
    (r"\bmanifestarse\b", ["verse", "notarse", "aparecer"]),
    (r"\bdenominar\b", ["llamar", "nombrar"]),
    (r"\bimpactar\b", ["afectar", "influir en", "repercutir en"]),
    (r"\bpotenciar\b", ["reforzar", "fortalecer", "impulsar"]),
    (r"\bdesarrollar\b", ["crear", "armar", "construir"]),
    (r"\bcomprender\b", ["entender", "captar"]),
    # Adjetivos / adverbios inflados
    (r"\bsignificativamente\b", ["bastante", "mucho", "de forma notable"]),
    (r"\bfundamentalmente\b", ["sobre todo", "básicamente", "en esencia"]),
    (r"\bactualmente\b", ["hoy", "ahora", "a día de hoy"]),
    (r"\badicional(?:mente)?\b", ["extra", "más", "aparte"]),
    (r"\bsubstancial(?:mente)?\b", ["grande", "considerablemente", "notable"]),
    (r"\bprimordial\b", ["principal", "central", "clave"]),
    (r"\binherente\b", ["propio", "natural", "intrínseco"]),
    (r"\bconsiderable\b", ["grande", "notable", "importante"]),
    (r"\bsumamente\b", ["muy", "bastante", "enormemente"]),
    (r"\bampliamente\b", ["mucho", "de sobra"]),
    (r"\bdiversos\b", ["varios", "distintos", "diferentes"]),
    (r"\bnumerosos\b", ["muchos", "varios", "bastantes"]),
    (r"\bespecíficamente\b", ["en concreto", "puntualmente"]),
    (r"\bprevia(?:mente)?\b", ["antes", "de antemano"]),
    (r"\bposterior(?:mente)?\b", ["después", "luego", "más adelante"]),
    # Sustantivos inflados
    (r"\bmetodología\b", ["método", "enfoque", "forma"]),
    (r"\bproblemática\b", ["problema", "situación", "tema"]),
    (r"\btemática\b", ["tema", "asunto"]),
    (r"\bparadigma\b", ["modelo", "enfoque", "esquema"]),
    (r"\bherramientas\b", ["recursos", "instrumentos", "medios"]),
    (r"\bámbito\b", ["campo", "área", "terreno"]),
    (r"\bcontexto\b", ["situación", "escenario", "entorno"]),
    (r"\benfoque\b", ["perspectiva", "visión", "punto de vista"]),
    # Conectores planos de IA
    (r"\bademás de ello\b,?", ["aparte de eso,", "sumando a eso,"]),
    (r"\bpor otra parte\b,?", ["por otro lado,", "también,"]),
    (r"\ben este sentido\b,?", ["en esa línea,", "bajo esa idea,"]),
    (r"\bcabe señalar que\b", ["hay que notar que", "vale aclarar que"]),
    (r"\bcabe mencionar que\b", ["vale decir que", "un dato importante es que"]),
    (r"\bes necesario\b", ["hace falta", "conviene", "hay que"]),
    (r"\bse puede(?:n)? observar\b", ["se nota", "se ve", "queda claro"]),
    (r"\bdicho lo anterior\b,?", ["con esto en mente,", "teniendo eso claro,"]),
    (r"\bde esta manera\b,?", ["así,", "con eso,"]),
    (r"\bde igual forma\b,?", ["del mismo modo,", "igualmente,"]),
    (r"\ben relación con\b", ["sobre", "respecto a", "acerca de"]),
    (r"\bcon respecto a\b", ["sobre", "en cuanto a"]),
    (r"\ba través de\b", ["mediante", "por medio de", "con"]),
    (r"\bcon el fin de\b", ["para", "con el objetivo de"]),
    (r"\bcon el propósito de\b", ["para", "buscando"]),
    (r"\ben función de\b", ["según", "dependiendo de"]),
    (r"\ba lo largo de\b", ["durante", "en"]),
]

_SINONIMOS_EN: list[tuple[str, list[str]]] = [
    (r"\butilize\b", ["use", "employ"]),
    (r"\bimplement\b", ["apply", "set up", "put in place"]),
    (r"\bfacilitate\b", ["help", "make easier", "support"]),
    (r"\boptimize\b", ["improve", "fine-tune"]),
    (r"\bleverage\b", ["use", "take advantage of"]),
    (r"\bensure\b", ["make sure", "confirm"]),
    (r"\benhance\b", ["improve", "boost", "strengthen"]),
    (r"\bdemonstrate\b", ["show", "prove", "reveal"]),
    (r"\bsignificantly\b", ["a lot", "considerably", "quite"]),
    (r"\bfundamentally\b", ["basically", "at its core"]),
    (r"\badditionally\b,?", ["also,", "on top of that,", "plus,"]),
    (r"\bfurthermore\b,?", ["also,", "besides,", "what's more,"]),
    (r"\bmoreover\b,?", ["on top of that,", "also,", "besides,"]),
    (r"\bnevertheless\b,?", ["still,", "even so,", "that said,"]),
    (r"\bnonetheless\b,?", ["still,", "even so,"]),
    (r"\bconsequently\b,?", ["so,", "as a result,", "because of that,"]),
    (r"\btherefore\b,?", ["so,", "that's why", "for that reason,"]),
    (r"\bsubsequently\b,?", ["then,", "after that,", "later,"]),
    (r"\bin order to\b", ["to"]),
    (r"\bwith respect to\b", ["about", "regarding"]),
    (r"\bwith regard to\b", ["about", "on"]),
    (r"\bin terms of\b", ["when it comes to", "for"]),
    (r"\bit is essential to\b", ["you need to", "it's key to"]),
    (r"\bit should be noted that\b", ["keep in mind that", "notably,"]),
    (r"\bmethodology\b", ["method", "approach"]),
    (r"\bparadigm\b", ["model", "framework", "approach"]),
]

# ---- Adverbios de relleno que la IA inyecta para sonar "más completo" ----
_ADVERBIOS_RELLENO = [
    r"\bindudablemente,?\s*",
    r"\bciertamente,?\s*",
    r"\bincuestionablemente,?\s*",
    r"\binnegablemente,?\s*",
    r"\bnotablemente,?\s*",
    r"\bparticularmente,?\s*",
    r"\bespecialmente,?\s*",
    r"\bdefinitivamente,?\s*",
    r"\besencialmente,?\s*",
    r"\bundoubtedly,?\s*",
    r"\bcertainly,?\s*",
    r"\bundeniably,?\s*",
    r"\bremarkably,?\s*",
    r"\bparticularly,?\s*",
    r"\bessentially,?\s*",
]

# ---- Conectores de subordinación para dividir oraciones largas ----
_CONJUNCIONES_CORTE_ES = [
    (", ya que ", ["Esto se debe a que ", "La razón es que ", "El motivo: "]),
    (", puesto que ", ["Esto ocurre porque ", "La causa es que "]),
    (", por lo que ", ["Por eso, ", "Esto lleva a que ", "De ahí que "]),
    (", debido a que ", ["La razón es que ", "Esto sucede porque "]),
    (", lo cual ", ["Esto ", "Eso "]),
    (", dado que ", ["La explicación: ", "Esto se debe a que "]),
    (", de modo que ", ["Así, ", "Esto hace que "]),
    (", de manera que ", ["Así, ", "Esto logra que "]),
    (", lo que permite ", ["Esto permite ", "Eso abre la puerta a "]),
    (", lo que implica ", ["Esto implica ", "Eso supone "]),
    (" mientras que ", ["En cambio, ", "Por otro lado, "]),
    (" aunque ", ["Sin embargo, ", "Eso sí, "]),
    (", sin embargo, ", ["Ahora bien, ", "Con todo, "]),
    (", no obstante, ", ["Aun así, ", "De todos modos, "]),
]

_CONJUNCIONES_CORTE_EN = [
    (", which means ", ["This means ", "So "]),
    (", as a result ", ["Because of this, ", "This leads to "]),
    (", because ", ["The reason: ", "This is because "]),
    (", since ", ["This is because ", "The reason being "]),
    (", therefore ", ["So, ", "As a result, "]),
    (", thus ", ["So, ", "This way, "]),
    (", whereas ", ["On the other hand, ", "In contrast, "]),
    (", although ", ["However, ", "That said, "]),
    (", however, ", ["Still, ", "But then, "]),
]


def _aplicar_sinonimos(texto: str, tabla: list[tuple[str, list[str]]], probabilidad: float = 0.70) -> str:
    """Reemplaza palabras/frases formales por sinónimos naturales con cierta probabilidad."""
    for pat, opciones in tabla:
        matches = list(re.finditer(pat, texto, flags=re.IGNORECASE))
        for m in reversed(matches):
            if random.random() > probabilidad:
                continue
            elegido = random.choice(opciones)
            original = m.group(0)
            # Preservar mayúscula
            if original and original[0].isupper():
                elegido = elegido[0].upper() + elegido[1:]
            texto = texto[:m.start()] + elegido + texto[m.end():]
    return texto


def _podar_adverbios_relleno(texto: str) -> str:
    """Elimina adverbios de relleno que la IA usa para inflar oraciones."""
    for pat in _ADVERBIOS_RELLENO:
        # Solo eliminar ~65% para que no quede demasiado seco
        matches = list(re.finditer(pat, texto, flags=re.IGNORECASE))
        for m in reversed(matches):
            if random.random() < 0.65:
                texto = texto[:m.start()] + texto[m.end():]
    return texto


def _dividir_oraciones_largas(oraciones: list[str], conjunciones: list) -> list[str]:
    """Divide oraciones que superan ~11 palabras usando conectores o comas."""
    resultado = []
    for oracion in oraciones:
        words = oracion.split()
        dividida = False
        if len(words) >= 11:
            for conj, inicios in conjunciones:
                if conj.lower() in oracion.lower():
                    idx_conj = oracion.lower().index(conj.lower())
                    p1 = oracion[:idx_conj].strip()
                    p2 = oracion[idx_conj + len(conj):].strip()
                    if len(p1.split()) >= 4 and len(p2.split()) >= 3:
                        p1_final = p1 if p1.endswith((".", "!", "?")) else p1 + "."
                        inicio = random.choice(inicios)
                        p2_final = inicio + p2[0].lower() + p2[1:]
                        if not p2_final.endswith((".", "!", "?")):
                            p2_final += "."
                        resultado.append(p1_final)
                        resultado.append(p2_final)
                        dividida = True
                        break

        # Fallback: si la oración tiene >= 13 palabras y tiene coma, dividir por coma
        if not dividida and len(words) >= 13 and ", " in oracion:
            comas = [i for i, ch in enumerate(oracion) if ch == ',']
            if comas:
                centro = len(oracion) // 2
                mejor_coma = min(comas, key=lambda c: abs(c - centro))
                p1 = oracion[:mejor_coma].strip()
                p2 = oracion[mejor_coma + 1:].strip()
                if len(p1.split()) >= 4 and len(p2.split()) >= 4:
                    p1_final = p1 if p1.endswith((".", "!", "?")) else p1 + "."
                    p2_final = p2[0].upper() + p2[1:]
                    if not p2_final.endswith((".", "!", "?")):
                        p2_final += "."
                    resultado.append(p1_final)
                    resultado.append(p2_final)
                    dividida = True

        if not dividida:
            resultado.append(oracion)
    return resultado


def _fusionar_oraciones_cortas(oraciones: list[str]) -> list[str]:
    """Fusiona pares de oraciones muy cortas (<7 palabras) para crear variación de ritmo."""
    if len(oraciones) < 2:
        return oraciones

    resultado = []
    i = 0
    while i < len(oraciones):
        o = oraciones[i]
        # Si esta oración y la siguiente son ambas cortas, fusionar con ~50% de prob
        if (i + 1 < len(oraciones)
                and len(o.split()) < 7
                and len(oraciones[i + 1].split()) < 7
                and random.random() < 0.50):
            next_o = oraciones[i + 1]
            # Quitar punto final de la primera
            o_sin_punto = o.rstrip(".!?")
            conectores_fusion = [" y ", " pero ", "; ", ", además "]
            conector = random.choice(conectores_fusion)
            fusionada = o_sin_punto + conector + next_o[0].lower() + next_o[1:]
            resultado.append(fusionada)
            i += 2
        else:
            resultado.append(o)
            i += 1
    return resultado


def _invertir_clausulas(oracion: str) -> str:
    """
    Si la oración tiene la forma 'A, conector B.', la reordena a 'Conector B, A.'
    Aplica con ~30% de probabilidad para no ser predecible.
    """
    if random.random() > 0.30:
        return oracion

    patrones_inversion = [
        r"^(.{15,}),\s*(por lo tanto|por eso|así que|de esta forma|en consecuencia)\s+(.+)$",
        r"^(.{15,}),\s*(sin embargo|no obstante|aunque|aun así)\s+(.+)$",
    ]
    for pat in patrones_inversion:
        m = re.match(pat, oracion, flags=re.IGNORECASE)
        if m:
            parte_a = m.group(1).strip().rstrip(".,")
            conector = m.group(2).strip()
            parte_b = m.group(3).strip().rstrip(".")
            invertida = f"{conector.capitalize()} {parte_b}, {parte_a[0].lower()}{parte_a[1:]}."
            return invertida
    return oracion


def _reescribir_pasiva_a_activa_es(oracion: str) -> str:
    """Convierte estructuras pasivas/impersonales comunes a voz activa."""
    if random.random() > 0.55:
        return oracion

    transformaciones = [
        (r"\bse ha demostrado que\b", ["la evidencia muestra que", "los datos confirman que", "queda claro que"]),
        (r"\bse ha observado que\b", ["se nota que", "es visible que", "se puede ver que"]),
        (r"\bse puede(?:n)? (?:ver|notar|observar|apreciar) que\b", ["es evidente que", "queda claro que"]),
        (r"\bha sido ampliamente reconocido que\b", ["se sabe bien que", "es conocido que"]),
        (r"\bes ampliamente reconocido que\b", ["se sabe que", "está claro que"]),
        (r"\bse estima que\b", ["los cálculos indican que", "se calcula que"]),
        (r"\bse evidencia que\b", ["queda claro que", "se nota que"]),
        (r"\bse sugiere que\b", ["todo apunta a que", "parece que"]),
        (r"\bse establece que\b", ["queda definido que", "se fija que"]),
        (r"\bse plantea que\b", ["surge la idea de que", "se propone que"]),
        (r"\bcabe resaltar que\b", ["un punto importante es que", "vale la pena ver que"]),
        (r"\bcabe recalcar que\b", ["hay que insistir en que", "no sobra repetir que"]),
        (r"\bes preciso (?:mencionar|indicar|señalar) que\b", ["hay que decir que", "vale aclarar que"]),
        (r"\bhas been demonstrated\b", ["the evidence shows", "data confirms"]),
        (r"\bit has been observed that\b", ["we can see that", "it's clear that"]),
        (r"\bit has been widely recognized\b", ["it's well known", "everyone agrees"]),
        (r"\bit can be seen that\b", ["clearly,", "as you can see,"]),
        (r"\bit is suggested that\b", ["it seems", "evidence points to"]),
    ]
    for pat, opciones in transformaciones:
        if re.search(pat, oracion, flags=re.IGNORECASE):
            elegido = random.choice(opciones)
            m = re.search(pat, oracion, flags=re.IGNORECASE)
            if m and m.group(0)[0].isupper():
                elegido = elegido[0].upper() + elegido[1:]
            oracion = re.sub(pat, elegido, oracion, count=1, flags=re.IGNORECASE)
            break
    return oracion


def _aplicar_estilo_personal_profundo(oraciones: list[str], perfil: dict) -> list[str]:
    """
    Aplica transferencia profunda de estilo basada en el perfil del usuario:
    - Adapta longitud de oraciones al ritmo del usuario
    - Inyecta conectores favoritos del usuario a lo largo del texto
    - Aplica persona gramatical y puntuación característica
    """
    if not perfil or not perfil.get("valido"):
        return oraciones

    resultado = list(oraciones)
    long_objetivo = perfil.get("longitud_media", 14.0)

    # A) Adaptar persona gramatical extensivamente
    if perfil["persona"] == "1a_singular":
        reemplazos = [
            (r"\bse puede observar\b", "puedo notar"),
            (r"\bse observa\b", "noto"),
            (r"\bse nota\b", "veo"),
            (r"\bse debe (?:tener en cuenta|considerar)\b", "creo que hay que considerar"),
            (r"\bresulta evidente\b", "tengo claro"),
            (r"\bse requiere\b", "necesito"),
            (r"\bse recomienda\b", "sugiero"),
            (r"\bse considera\b", "considero"),
            (r"\bse puede(?:n)? (?:afirmar|decir|concluir)\b", "puedo decir"),
            (r"\bes posible (?:afirmar|concluir)\b", "me parece que"),
            (r"\bes importante\b", "para mí es clave"),
            (r"\bse destaca\b", "destaco"),
            (r"\bse evidencia\b", "veo claro"),
            (r"\bse ha demostrado\b", "he notado"),
            (r"\bse ha comprobado\b", "he comprobado"),
            (r"\bse identificó\b", "identifiqué"),
            (r"\bse encontró\b", "encontré"),
            (r"\bse determinó\b", "determiné"),
            (r"\bse analizó\b", "analicé"),
            (r"\bse evaluó\b", "evalué"),
            (r"\bse obtuvo\b", "obtuve"),
            (r"\bse logró\b", "logré"),
            (r"\bse realizó\b", "realicé"),
            (r"\bse verificó\b", "verifiqué"),
            (r"\bse concluyó\b", "concluí"),
            (r"\bse propone\b", "propongo"),
            (r"\bse busca\b", "busco"),
            (r"\bse pretende\b", "pretendo"),
            (r"\bse espera\b", "espero"),
        ]
        for idx, o in enumerate(resultado):
            for p_from, p_to in reemplazos:
                m = re.search(p_from, o, flags=re.IGNORECASE)
                if m:
                    repl = p_to
                    if m.group(0)[0].isupper():
                        repl = repl[0].upper() + repl[1:]
                    resultado[idx] = re.sub(p_from, repl, resultado[idx], count=1, flags=re.IGNORECASE)

    elif perfil["persona"] == "1a_plural":
        reemplazos = [
            (r"\bse puede observar\b", "podemos ver"),
            (r"\bse observa\b", "observamos"),
            (r"\bse nota\b", "notamos"),
            (r"\bse debe (?:tener en cuenta|considerar)\b", "debemos considerar"),
            (r"\bresulta evidente\b", "nos queda claro"),
            (r"\bse requiere\b", "necesitamos"),
            (r"\bse recomienda\b", "sugerimos"),
            (r"\bse considera\b", "consideramos"),
            (r"\bse puede(?:n)? (?:afirmar|decir|concluir)\b", "podemos afirmar"),
            (r"\bes posible (?:afirmar|concluir)\b", "podemos concluir"),
            (r"\bes importante\b", "para nosotros es clave"),
            (r"\bse destaca\b", "destacamos"),
            (r"\bse evidencia\b", "vemos claro"),
            (r"\bse ha demostrado\b", "hemos comprobado"),
            (r"\bse ha comprobado\b", "hemos verificado"),
            (r"\bse identificó\b", "identificamos"),
            (r"\bse encontró\b", "encontramos"),
            (r"\bse determinó\b", "determinamos"),
            (r"\bse analizó\b", "analizamos"),
            (r"\bse evaluó\b", "evaluamos"),
            (r"\bse obtuvo\b", "obtuvimos"),
            (r"\bse logró\b", "logramos"),
            (r"\bse realizó\b", "realizamos"),
            (r"\bse verificó\b", "verificamos"),
            (r"\bse concluyó\b", "concluimos"),
            (r"\bse propone\b", "proponemos"),
            (r"\bse busca\b", "buscamos"),
            (r"\bse pretende\b", "pretendemos"),
            (r"\bse espera\b", "esperamos"),
        ]
        for idx, o in enumerate(resultado):
            for p_from, p_to in reemplazos:
                m = re.search(p_from, o, flags=re.IGNORECASE)
                if m:
                    repl = p_to
                    if m.group(0)[0].isupper():
                        repl = repl[0].upper() + repl[1:]
                    resultado[idx] = re.sub(p_from, repl, resultado[idx], count=1, flags=re.IGNORECASE)

    # B) Inyectar conectores favoritos del usuario a lo largo del texto
    conectores = perfil.get("conectores_detectados", [])
    if conectores and len(resultado) >= 3:
        # Inyectar en varias posiciones (no solo la segunda oración)
        posiciones = list(range(1, len(resultado), max(1, len(resultado) // (len(conectores) + 1))))
        for i, pos in enumerate(posiciones):
            if pos >= len(resultado):
                break
            conector = conectores[i % len(conectores)].capitalize()
            o = resultado[pos]
            # Solo si la oración no empieza con un conector ya
            inicios_existentes = ("De hecho", "Por eso", "Además", "Sin embargo", "La verdad",
                                  "O sea", "Es decir", "Ojo", "En cambio", "Así que", "¿")
            if not o.startswith(inicios_existentes):
                resultado[pos] = f"{conector}, {o[0].lower()}{o[1:]}"

    # C) Preguntas retóricas si el usuario las usa
    if perfil.get("puntuacion", {}).get("usa_preguntas"):
        preguntas_retor = [
            "¿Y por qué importa esto?",
            "¿Qué significa eso en la práctica?",
            "¿Cuál es la clave aquí?",
            "¿Qué nos dice esto realmente?",
            "¿Y eso qué implica?",
        ]
        # Insertar 1-2 preguntas retóricas si el texto no tiene ninguna
        tiene_preguntas = any("?" in o for o in resultado)
        if not tiene_preguntas and len(resultado) >= 4:
            pos = random.randint(1, min(3, len(resultado) - 1))
            resultado.insert(pos, random.choice(preguntas_retor))

    # D) Puntos suspensivos si el usuario los usa
    if perfil.get("puntuacion", {}).get("usa_puntos_suspensivos") and len(resultado) >= 3:
        idx = random.randint(0, len(resultado) - 1)
        o = resultado[idx]
        if o.endswith("."):
            resultado[idx] = o[:-1] + "..."

    # E) Guiones si el usuario los usa
    if perfil.get("puntuacion", {}).get("usa_guiones"):
        for idx, o in enumerate(resultado):
            if ", " in o and random.random() < 0.25:
                resultado[idx] = o.replace(", ", " — ", 1)
                break

    # F) Ajustar longitud media de oraciones al ritmo del usuario
    # Si el usuario escribe frases cortas (< 12 palabras), intentar acortar más
    if long_objetivo < 12:
        nuevas = []
        for o in resultado:
            words = o.split()
            if len(words) > 15 and ", " in o:
                partes = o.split(", ", 1)
                p1 = partes[0].strip()
                p2 = partes[1].strip()
                if len(p1.split()) >= 4 and len(p2.split()) >= 4:
                    p1_final = p1 if p1.endswith((".", "!", "?")) else p1 + "."
                    p2_final = p2[0].upper() + p2[1:]
                    if not p2_final.endswith((".", "!", "?")):
                        p2_final += "."
                    nuevas.append(p1_final)
                    nuevas.append(p2_final)
                    continue
            nuevas.append(o)
        resultado = nuevas

    # G) Si el usuario tiene registro casual, informalizar aún más
    if perfil.get("registro") == "casual":
        casual_extra = [
            (r"\bes necesario\b", ["toca", "hay que", "hace falta"]),
            (r"\bse evidencia\b", ["se ve", "se nota"]),
            (r"\bdado que\b", ["como", "ya que"]),
            (r"\bpor tanto\b,?", ["así que", "entonces"]),
            (r"\bmediante\b", ["con", "a través de"]),
        ]
        for idx, o in enumerate(resultado):
            for pat, opciones in casual_extra:
                if re.search(pat, o, flags=re.IGNORECASE):
                    resultado[idx] = re.sub(pat, random.choice(opciones), resultado[idx], count=1, flags=re.IGNORECASE)

    return resultado


def _diversificar_inicios(oraciones: list[str]) -> list[str]:
    """
    Cambia los inicios repetitivos de oraciones para romper patrones de IA.
    Si varias oraciones empiezan con artículos/pronombres similares, reformula el inicio.
    """
    if len(oraciones) < 3:
        return oraciones

    resultado = list(oraciones)

    prefijos_es = [
        "La verdad es que ", "En la práctica, ", "Por su parte, ",
        "Hoy en día, ", "Mirándolo bien, ", "Al respecto, ",
        "De entrada, ", "Con todo esto, ", "Ojo: ", "En el fondo, ",
        "Ahora bien, ", "Eso sí, ", "Un dato clave: "
    ]
    prefijos_en = [
        "In practice, ", "The thing is, ", "Looking closely, ",
        "For its part, ", "Right now, ", "One key point: ",
        "Worth noting, ", "That said, ", "Here's the thing: "
    ]

    articulos_vistos = 0
    for i, o in enumerate(resultado):
        words = o.split()
        if not words or len(words) < 4:
            continue
        first = words[0].lower()
        # Evitar modificar frases hechas como "la verdad", "lo cierto", "el tema"
        if len(words) >= 2 and (first, words[1].lower()) in [("la", "verdad"), ("lo", "cierto"), ("el", "tema"), ("al", "final")]:
            continue
        if first in ("el", "la", "los", "las", "un", "una", "este", "esta", "the", "this", "these", "it", "they"):
            articulos_vistos += 1
            if articulos_vistos > 1 and random.random() < 0.70:
                es_ingles = any(w.lower() in ("the", "this", "it", "they", "we", "is", "are", "has") for w in words[:5])
                prefijo = random.choice(prefijos_en if es_ingles else prefijos_es)
                resto = words[0].lower() + " " + " ".join(words[1:])
                resultado[i] = prefijo + resto
    return resultado


def _inyectar_imperfecciones_humanas(oraciones: list[str]) -> list[str]:
    """
    Inyecta imperfecciones naturales del habla humana:
    fragmentos, interjecciones, paréntesis, contracciones.
    """
    if len(oraciones) < 4:
        return oraciones

    resultado = list(oraciones)

    # Interjecciones/muletillas que se insertan ocasionalmente
    muletillas_es = [
        "Bueno, ", "Ojo, ", "Mira, ", "A ver, ", "Vamos, ",
        "Claro, ", "En fin, ",
    ]
    muletillas_en = [
        "Well, ", "Look, ", "Sure, ", "I mean, ", "Right, ",
    ]

    conectores_bloqueo = (
        "bueno", "ojo", "mira", "a ver", "vamos", "claro", "en fin",
        "well", "look", "sure", "la verdad", "de hecho", "por eso",
        "al final", "en el fondo", "eso sí", "ahora bien", "es decir", "o sea"
    )

    # Insertar 1-2 muletillas en posiciones aleatorias
    inserciones = 0
    for i in range(1, len(resultado) - 1):
        if inserciones >= 2:
            break
        o = resultado[i]
        # No insertar si ya empieza con un conector o muletilla
        if any(o.lower().startswith(cb) for cb in conectores_bloqueo):
            continue
        if random.random() < 0.18:
            es_ingles = any(w in o.lower().split()[:4] for w in ("the", "is", "are", "has", "it"))
            muletilla = random.choice(muletillas_en if es_ingles else muletillas_es)
            resultado[i] = muletilla + o[0].lower() + o[1:]
            inserciones += 1

    # Convertir alguna oración larga en una con paréntesis
    for i in range(len(resultado)):
        o = resultado[i]
        if len(o.split()) > 12 and ", " in o and random.random() < 0.20:
            # Encontrar una cláusula subordinada para poner entre paréntesis
            partes = o.split(", ", 2)
            if len(partes) >= 3 and len(partes[1].split()) >= 3:
                resultado[i] = f"{partes[0]} ({partes[1]}) {partes[2]}"
            break

    return resultado


def _eliminar_transiciones_excesivas(oraciones: list[str]) -> list[str]:
    """
    Elimina o simplifica transiciones formales excesivas que la IA inyecta.
    """
    transiciones_eliminar = [
        (r"^Además,?\s+", ""),
        (r"^Asimismo,?\s+", ""),
        (r"^De igual forma,?\s+", ""),
        (r"^De igual manera,?\s+", ""),
        (r"^En este sentido,?\s+", ""),
        (r"^Dicho lo anterior,?\s+", ""),
        (r"^Additionally,?\s+", ""),
        (r"^Furthermore,?\s+", ""),
        (r"^Moreover,?\s+", ""),
    ]

    resultado = list(oraciones)
    eliminadas = 0
    for i in range(len(resultado)):
        if eliminadas >= 3:
            break
        for pat, repl in transiciones_eliminar:
            if re.match(pat, resultado[i], flags=re.IGNORECASE):
                if random.random() < 0.65:
                    nuevo = re.sub(pat, repl, resultado[i], count=1, flags=re.IGNORECASE)
                    if nuevo:
                        nuevo = nuevo[0].upper() + nuevo[1:]
                    resultado[i] = nuevo
                    eliminadas += 1
                break
    return resultado


def _una_pasada_humanizacion(texto: str, modo: str, nivel: str, perfil_usuario: dict | None) -> str:
    """Ejecuta una pasada completa de humanización sobre el texto."""
    texto_proc = texto

    # ── CAPA 1: Erradicar clichés robóticos ──
    for pat, reemplazos in REEMPLAZOS_CLICHES_ES + REEMPLAZOS_CLICHES_EN:
        if isinstance(reemplazos, list):
            matches = list(re.finditer(pat, texto_proc, flags=re.IGNORECASE))
            for m in reversed(matches):
                elegido = random.choice(reemplazos)
                if m.group(0) and m.group(0)[0].isupper():
                    elegido = elegido[0].upper() + elegido[1:]
                texto_proc = texto_proc[:m.start()] + elegido + texto_proc[m.end():]
        elif isinstance(reemplazos, str):
            texto_proc = re.sub(pat, reemplazos, texto_proc, flags=re.IGNORECASE)

    # ── CAPA 1.5: Verbos y fórmulas pasivas extendidas ──
    for pat, opciones in _PASIVAS_EXTENDIDAS_ES + _PASIVAS_EXTENDIDAS_EN:
        matches = list(re.finditer(pat, texto_proc, flags=re.IGNORECASE))
        for m in reversed(matches):
            elegido = random.choice(opciones)
            if m.group(0) and m.group(0)[0].isupper():
                elegido = elegido[0].upper() + elegido[1:]
            texto_proc = texto_proc[:m.start()] + elegido + texto_proc[m.end():]

    # ── CAPA 2: Sustitución amplia de vocabulario formal → natural ──
    texto_proc = _aplicar_sinonimos(texto_proc, _SINONIMOS_ES, probabilidad=0.85)
    texto_proc = _aplicar_sinonimos(texto_proc, _SINONIMOS_EN, probabilidad=0.85)

    # ── CAPA 3: Podar adverbios de relleno ──
    texto_proc = _podar_adverbios_relleno(texto_proc)

    # ── CAPA 4: Reescribir pasivas/impersonales a voz activa ──
    oraciones = dividir_en_oraciones(texto_proc)
    oraciones = [_reescribir_pasiva_a_activa_es(o) for o in oraciones]

    # ── CAPA 5: Dividir oraciones largas y monótonas ──
    oraciones = _dividir_oraciones_largas(oraciones, _CONJUNCIONES_CORTE_ES + _CONJUNCIONES_CORTE_EN)

    # ── CAPA 6: Fusionar oraciones cortas consecutivas para crear contraste ──
    if len(oraciones) >= 3 and random.random() < 0.60:
        idx_f = random.randint(0, len(oraciones) - 2)
        o1 = oraciones[idx_f].rstrip(".!?")
        o2 = oraciones[idx_f + 1]
        conector_f = random.choice(["; de hecho, ", "; además, ", " —y ", ", por lo que "])
        fusion = o1 + conector_f + o2[0].lower() + o2[1:]
        oraciones = oraciones[:idx_f] + [fusion] + oraciones[idx_f + 2:]
    else:
        oraciones = _fusionar_oraciones_cortas(oraciones)

    # ── CAPA 7: Invertir cláusulas para romper el orden predecible ──
    oraciones = [_invertir_clausulas(o) for o in oraciones]

    # ── CAPA 8: Diversificar inicios de oraciones ──
    oraciones = _diversificar_inicios(oraciones)

    # ── CAPA 9: Eliminar transiciones formales excesivas ──
    oraciones = _eliminar_transiciones_excesivas(oraciones)

    # ── CAPA 10: Inyectar imperfecciones humanas o micro-oraciones punchline ──
    oraciones = _inyectar_imperfecciones_humanas(oraciones)
    longitudes = [len(o.split()) for o in oraciones]
    desv = statistics.stdev(longitudes) if len(longitudes) > 1 else 1.0
    if desv < 4.5 and len(oraciones) >= 2 and random.random() < 0.75:
        es_en = any("the " in o.lower() for o in oraciones)
        punch = random.choice(_PUNCH_LINES_EN if es_en else _PUNCH_LINES_ES)
        pos = random.randint(1, len(oraciones) - 1)
        oraciones.insert(pos, punch)

    # ── CAPA 11: Aplicar estilo personal o ajustes de nivel ──
    if modo == "estilo_personal":
        oraciones = _aplicar_estilo_personal_profundo(oraciones, perfil_usuario)
    elif modo == "automatico":
        if nivel == "casual":
            casual_map = [
                (r"\ben la actualidad\b,?", ["hoy por hoy,", "a día de hoy,"]),
                (r"\bconviene notar que\b", ["la verdad es que", "lo cierto es que"]),
                (r"\bes indispensable\b", ["hace mucha falta", "es súper necesario"]),
                (r"\bse requiere\b", ["hace falta", "se necesita"]),
                (r"\bes necesario\b", ["toca", "hay que"]),
                (r"\bmediante\b", ["con", "usando"]),
                (r"\bno obstante\b,?", ["pero bueno,", "eso sí,"]),
            ]
            for idx, o in enumerate(oraciones):
                for r_pat, r_opciones in casual_map:
                    if re.search(r_pat, o, flags=re.IGNORECASE):
                        oraciones[idx] = re.sub(r_pat, random.choice(r_opciones), oraciones[idx], count=1, flags=re.IGNORECASE)
        elif nivel == "academico":
            acad_map = [
                (r"\bhoy en día\b,?", ["en el contexto actual,", "en el marco contemporáneo,"]),
                (r"\bde hecho\b,?", ["en efecto,", "en este sentido,"]),
                (r"\bhay que\b", ["es preciso", "conviene"]),
                (r"\bse ve\b", ["se evidencia", "se aprecia"]),
            ]
            for idx, o in enumerate(oraciones):
                for r_pat, r_opciones in acad_map:
                    if re.search(r_pat, o, flags=re.IGNORECASE):
                        oraciones[idx] = re.sub(r_pat, random.choice(r_opciones), oraciones[idx], count=1, flags=re.IGNORECASE)

    texto_humanizado = " ".join(oraciones).strip()

    # Limpieza final
    texto_humanizado = re.sub(r'  +', ' ', texto_humanizado)
    texto_humanizado = re.sub(r'\.{2}(?!\.)', '.', texto_humanizado)
    texto_humanizado = re.sub(r',\s*\.', '.', texto_humanizado)
    texto_humanizado = re.sub(r'\.\s*,', '.', texto_humanizado)

    return texto_humanizado


def humanizar_texto(
    texto: str,
    modo: str = "automatico",
    nivel: str = "equilibrado",
    texto_muestra_usuario: str = ""
) -> dict:
    """
    Humaniza un texto mediante búsqueda estocástica multivariante (hill-climbing).
    Genera múltiples candidatos por ronda y selecciona iterativamente la versión
    que minimiza la probabilidad de detección por IA hacia valores cercanos a 0%.
    """
    if not texto or not texto.strip():
        return {
            "texto_humanizado": "",
            "puntuacion_antes": 0,
            "puntuacion_despues": 0,
            "reduccion_porcentual": 0,
            "analisis_inicial": None,
            "analisis_final": None,
            "perfil_usuario": None,
            "modo_aplicado": modo,
            "nivel_aplicado": nivel,
        }

    analisis_inicial = analizar_texto_ia(texto)
    perfil_usuario = extraer_perfil_estilo(texto_muestra_usuario) if texto_muestra_usuario else None

    mejor_texto = texto
    mejor_score = analisis_inicial["puntuacion_ia"]
    mejor_analisis = analisis_inicial
    objetivo_score = 15
    num_candidatos_por_ronda = 10
    max_rondas = 5

    for ronda in range(max_rondas):
        if mejor_score <= objetivo_score:
            break

        candidatos = []
        for _ in range(num_candidatos_por_ronda):
            cand = _una_pasada_humanizacion(mejor_texto, modo, nivel, perfil_usuario)
            if cand.strip() and cand.strip() != mejor_texto.strip():
                c_analisis = analizar_texto_ia(cand)
                candidatos.append((c_analisis["puntuacion_ia"], cand, c_analisis))

        if not candidatos:
            break

        candidatos.sort(key=lambda x: x[0])
        top_score, top_cand, top_analisis = candidatos[0]

        if top_score < mejor_score:
            mejor_score = top_score
            mejor_texto = top_cand
            mejor_analisis = top_analisis
        else:
            # Si en esta ronda no mejoró pero ya se redujo el score, terminar
            break

    # Garantía absoluta: si por alguna razón el texto final fuera idéntico al original,
    # forzar al menos una transformación válida
    if mejor_texto.strip() == texto.strip() and texto.strip():
        cand_forzado = _una_pasada_humanizacion(texto, modo, nivel, perfil_usuario)
        if cand_forzado.strip():
            mejor_texto = cand_forzado
            mejor_analisis = analizar_texto_ia(mejor_texto)
            mejor_score = mejor_analisis["puntuacion_ia"]

    p_antes = analisis_inicial["puntuacion_ia"]
    p_despues = mejor_score
    reduccion = max(0, p_antes - p_despues)

    return {
        "texto_humanizado": mejor_texto,
        "puntuacion_antes": p_antes,
        "puntuacion_despues": p_despues,
        "reduccion_porcentual": reduccion,
        "analisis_inicial": analisis_inicial,
        "analisis_final": mejor_analisis,
        "perfil_usuario": perfil_usuario,
        "modo_aplicado": modo,
        "nivel_aplicado": nivel,
    }

