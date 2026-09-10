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

# Sustitutos naturales para la humanización
REEMPLAZOS_CLICHES_ES = [
    (r"\ben el vertiginoso mundo actual\b,?", ["hoy en día,", "en la actualidad,", "con el ritmo que llevamos hoy,"]),
    (r"\ben el vertiginoso mundo de\b", ["en el entorno de", "dentro de"]),
    (r"\bjuega un papel (crucial|fundamental|clave)\b", ["es esencial", "marca la diferencia", "resulta decisivo", "tiene un gran impacto"]),
    (r"\bdesempeña un papel (crucial|fundamental|clave)\b", ["es vital", "influye directamente", "marca la pauta"]),
    (r"\bes importante destacar que\b", ["conviene notar que", "llama la atención que", "la clave está en que", "hay que ver que"]),
    (r"\bes importante señalar que\b", ["vale recalcar que", "un punto a considerar es que", "ojo con que"]),
    (r"\bvale la pena mencionar que\b", ["un detalle interesante es que", "también cuenta que"]),
    (r"\bun tapiz de\b", ["una combinación de", "un conjunto de", "una mezcla de"]),
    (r"\bun abanico de posibilidades\b", ["muchas opciones", "distintas alternativas", "varios caminos"]),
    (r"\bforjando el camino\b", ["abriendo paso", "marcando el rumbo", "dando pie"]),
    (r"\bresulta fundamental\b", ["es indispensable", "hace falta", "conviene"]),
    (r"\bde vital importancia\b", ["muy valioso", "prioritario", "clave"]),
    (r"\ben conclusión\b,?", ["al final del día,", "en pocas palabras,", "en definitiva,"]),
    (r"\ben resumen\b,?", ["en pocas palabras,", "en concreto,", "básicamente,"]),
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
    (r"\bit is important to note that\b", ["it's worth noting that", "keep in mind that", "notably,"]),
    (r"\bplays a (crucial|pivotal) role\b", ["is key", "makes a big difference", "matters deeply"]),
    (r"\ba tapestry of\b", ["a rich mix of", "a wide variety of"]),
    (r"\ba myriad of\b", ["plenty of", "many", "various"]),
    (r"\bdelve into\b", ["explore", "look into", "examine"]),
    (r"\bin today's fast-paced world\b,?", ["nowadays,", "today,", "in modern times,"]),
    (r"\bnavigating the complexities of\b", ["dealing with", "tackling", "managing"]),
    (r"\bever-evolving\b", ["changing", "dynamic", "fast-moving"]),
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
    Los textos de IA tienen muy baja varianza (ritmo monótono).
    Los humanos tienen alta varianza (frases cortas mezcladas con compuestas).
    """
    if not longitudes:
        return 0.0, 0.0, 50.0
    media = statistics.mean(longitudes)
    if len(longitudes) < 2:
        return media, 0.0, 50.0
    desv = statistics.stdev(longitudes)

    # Coeficiente de variación (CV = desv / media)
    cv = desv / max(1.0, media)
    if desv < 3.0 or cv < 0.22:
        score = 88.0  # Muy uniforme -> probable IA
    elif desv < 5.0 or cv < 0.35:
        score = 70.0
    elif desv < 7.5 or cv < 0.50:
        score = 45.0
    elif desv < 10.0:
        score = 25.0
    else:
        score = 8.0  # Gran variabilidad de ritmo -> humano

    return round(media, 1), round(desv, 1), score


def calcular_riqueza_lexica(texto: str) -> tuple[float, float]:
    """
    Calcula el Type-Token Ratio (TTR) y devuelve el TTR y el score de IA derivado.
    """
    palabras = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+\b', texto.lower())
    total_tokens = len(palabras)
    if not total_tokens:
        return 0.0, 50.0
    tokens_unicos = len(set(palabras))
    ttr = tokens_unicos / total_tokens

    # Textos largos de IA tienden a un TTR moderado/plano (0.45 a 0.60)
    if total_tokens > 60:
        if 0.45 <= ttr <= 0.62:
            score = 65.0
        elif ttr < 0.45:
            score = 75.0
        else:
            score = 25.0
    else:
        score = 40.0

    return round(ttr * 100, 1), score


# ==============================================================================
# MOTOR PRINCIPAL DE DETECCIÓN DE IA
# ==============================================================================

def analizar_texto_ia(texto: str) -> dict:
    """
    Analiza un texto y devuelve su porcentaje de probabilidad de IA,
    métricas lingüísticas y un desglose detallado de cada oración.
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

    # 1. Burstiness
    media_long, desv_long, score_burstiness = calcular_burstiness(longitudes)

    # 2. Clichés y marcadores
    cliches_totales = []
    lista_patrones = CLICHES_IA_ES + CLICHES_IA_EN
    for pat in lista_patrones:
        coincidencias = re.findall(pat, texto, flags=re.IGNORECASE)
        if coincidencias:
            nombre_limpio = pat.replace(r"\b", "").replace(",?", "").replace(r"\s+", " ")
            cliches_totales.extend([nombre_limpio] * len(coincidencias))

    densidad_cliches = (len(cliches_totales) / max(1, total_palabras)) * 100
    if densidad_cliches > 1.6:
        score_cliches = 95.0
    elif densidad_cliches > 1.0:
        score_cliches = 82.0
    elif densidad_cliches > 0.4:
        score_cliches = 58.0
    elif densidad_cliches > 0.1:
        score_cliches = 32.0
    else:
        score_cliches = 6.0

    # 3. Riqueza léxica
    ttr_pct, score_ttr = calcular_riqueza_lexica(texto)

    # 4. Puntuación Global Ponderada
    puntuacion_ia = round(
        (score_burstiness * 0.40) +
        (score_cliches * 0.45) +
        (score_ttr * 0.15)
    )
    puntuacion_ia = max(2, min(98, puntuacion_ia))

    # Calificación cualitativa
    if puntuacion_ia >= 72:
        etiqueta = "Altamente probable de IA"
        color = "#EF4444"  # Rojo
        resumen = "El texto muestra una cadencia sintáctica muy regular y patrones léxicos típicos de modelos de lenguaje."
    elif puntuacion_ia >= 48:
        etiqueta = "Sospecha moderada / Mixto"
        color = "#F59E0B"  # Naranja
        resumen = "El texto contiene una combinación de frases naturales con algunas muletillas y estructuras predecibles."
    elif puntuacion_ia >= 25:
        etiqueta = "Probablemente Humano"
        color = "#3B82F6"  # Azul
        resumen = "La variación de longitud y la naturalidad sugieren redacción humana con mínima o nula asistencia de IA."
    else:
        etiqueta = "100% Humano"
        color = "#10B981"  # Verde
        resumen = "Excelente ritmo orgánico, rica variación de oraciones y ausencia de clichés automatizados."

    # 5. Evaluación individual de cada oración
    oraciones_analizadas = []
    for idx, o in enumerate(oraciones):
        o_words = len(o.split())
        cliches_en_o = []
        for pat in lista_patrones:
            if re.search(pat, o, flags=re.IGNORECASE):
                cliches_en_o.append(pat.replace(r"\b", "").replace(",?", ""))

        o_score = 15.0
        # Presencia de clichés suma directamente
        if cliches_en_o:
            o_score += 42.0 * len(cliches_en_o)
        # Rango canónico de longitud monótona en IA (16 a 25 palabras)
        if 16 <= o_words <= 25:
            o_score += 24.0
        elif o_words < 8 or o_words > 32:
            o_score -= 16.0

        o_score = max(3, min(99, round(o_score)))

        if o_score >= 65:
            nivel = "ia"
        elif o_score >= 40:
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
# MOTOR DE HUMANIZACIÓN DE TEXTO
# ==============================================================================

def humanizar_texto(
    texto: str,
    modo: str = "automatico",
    nivel: str = "equilibrado",
    texto_muestra_usuario: str = ""
) -> dict:
    """
    Humaniza un texto de entrada:
    - Modo 'automatico': erradica clichés de IA, rompe monotonía e inyecta burstiness natural.
    - Modo 'estilo_personal': adapta la voz, ritmo, conectores y persona del usuario a partir de su muestra.
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
        }

    analisis_inicial = analizar_texto_ia(texto)
    perfil_usuario = extraer_perfil_estilo(texto_muestra_usuario) if texto_muestra_usuario else None

    texto_proc = texto

    # 1. Erradicar clichés y muletillas robóticas (Español e Inglés)
    for pat, reemplazos in REEMPLAZOS_CLICHES_ES + REEMPLAZOS_CLICHES_EN:
        if isinstance(reemplazos, list):
            matches = list(re.finditer(pat, texto_proc, flags=re.IGNORECASE))
            for m in reversed(matches):
                elegido = random.choice(reemplazos)
                # Conservar mayúscula si iniciaba la frase
                if m.group(0) and m.group(0)[0].isupper():
                    elegido = elegido.capitalize()
                texto_proc = texto_proc[:m.start()] + elegido + texto_proc[m.end():]
        elif isinstance(reemplazos, str):
            texto_proc = re.sub(pat, reemplazos, texto_proc, flags=re.IGNORECASE)

    # 2. Inyección de Burstiness (Romper oraciones uniformes y monótonas)
    oraciones = dividir_en_oraciones(texto_proc)
    oraciones_nuevas = []

    for oracion in oraciones:
        words = oracion.split()

        # Si una oración excede las 20 palabras y tiene conectores de subordinación, dividirla
        conjunciones_corte = [
            ", ya que ", ", puesto que ", ", por lo que ", ", debido a que ",
            ", lo cual ", ", dado que ", ", de modo que "
        ]
        partida = False
        if len(words) > 19:
            for conj in conjunciones_corte:
                if conj in oracion:
                    partes = oracion.split(conj, 1)
                    p1 = partes[0].strip()
                    p2 = partes[1].strip()
                    if p1 and p2 and len(p1.split()) >= 4 and len(p2.split()) >= 4:
                        if "debido" in conj or "puesto" in conj or "ya que" in conj:
                            conector_2 = "Esto se debe a que "
                        else:
                            conector_2 = "Esto permite que "
                        
                        p1_final = p1 if p1.endswith((".", "!", "?")) else p1 + "."
                        p2_final = conector_2 + p2[0].lower() + p2[1:]
                        if not p2_final.endswith((".", "!", "?")):
                            p2_final += "."

                        oraciones_nuevas.append(p1_final)
                        oraciones_nuevas.append(p2_final)
                        partida = True
                        break
        
        if not partida:
            oraciones_nuevas.append(oracion)

    # 3. Aplicar Estilo Personal si el usuario proporcionó una muestra
    if modo == "estilo_personal" and perfil_usuario and perfil_usuario.get("valido"):
        # A) Adaptar persona gramatical
        if perfil_usuario["persona"] == "1a_singular":
            reemplazos_yo = [
                (r"\bse puede observar que\b", "puedo notar que"),
                (r"\bse debe tener en cuenta que\b", "en mi opinión conviene considerar que"),
                (r"\bresulta evidente que\b", "tengo claro que"),
                (r"\bse requiere\b", "necesito"),
                (r"\bse recomienda\b", "sugiero"),
                (r"\bse considera que\b", "considero que"),
            ]
            for idx, o in enumerate(oraciones_nuevas):
                for p_imp, p_yo in reemplazos_yo:
                    if re.search(p_imp, o, flags=re.IGNORECASE):
                        oraciones_nuevas[idx] = re.sub(p_imp, p_yo, o, flags=re.IGNORECASE)
                        break
        elif perfil_usuario["persona"] == "1a_plural":
            reemplazos_nos = [
                (r"\bse puede observar que\b", "podemos ver que"),
                (r"\bse debe tener en cuenta que\b", "debemos tener presente que"),
                (r"\bresulta evidente que\b", "vemos con claridad que"),
                (r"\bse requiere\b", "necesitamos"),
            ]
            for idx, o in enumerate(oraciones_nuevas):
                for p_imp, p_nos in reemplazos_nos:
                    if re.search(p_imp, o, flags=re.IGNORECASE):
                        oraciones_nuevas[idx] = re.sub(p_imp, p_nos, o, flags=re.IGNORECASE)
                        break

        # B) Si el usuario tiene conectores favoritos específicos, inyectar uno orgánicamente
        if perfil_usuario.get("conectores_detectados") and len(oraciones_nuevas) >= 2:
            conector_fav = perfil_usuario["conectores_detectados"][0].capitalize()
            # Añadirlo como transición en la segunda oración si no tiene conector inicial
            o2 = oraciones_nuevas[1]
            if not o2.startswith(("De hecho", "Por eso", "Además", "Sin embargo", "¿")):
                oraciones_nuevas[1] = f"{conector_fav}, {o2[0].lower()}{o2[1:]}"

        # C) Si el usuario acostumbra usar preguntas retóricas
        if perfil_usuario.get("puntuacion", {}).get("usa_preguntas") and len(oraciones_nuevas) >= 3:
            if not any("?" in o or "¿" in o for o in oraciones_nuevas):
                oraciones_nuevas.insert(1, "¿Por qué resulta esto tan determinante?")

    # 4. Ajustes por nivel seleccionado en modo automático
    elif modo == "automatico":
        if nivel == "casual":
            # Frases más directas, conectores coloquiales
            reemplazos_casual = [
                (r"\ben la actualidad,\b", "hoy por hoy,"),
                (r"\bconviene notar que\b", "la verdad es que"),
                (r"\bes indispensable\b", "hace mucha falta"),
            ]
            for idx, o in enumerate(oraciones_nuevas):
                for r_ant, r_cas in reemplazos_casual:
                    oraciones_nuevas[idx] = re.sub(r_ant, r_cas, oraciones_nuevas[idx], flags=re.IGNORECASE)
        elif nivel == "academico":
            # Estructura más sobria y formal pero sin clichés de ChatGPT
            reemplazos_acad = [
                (r"\bhoy en día,\b", "en el contexto actual,"),
                (r"\bde hecho,\b", "en este sentido,"),
            ]
            for idx, o in enumerate(oraciones_nuevas):
                for r_ant, r_acad in reemplazos_acad:
                    oraciones_nuevas[idx] = re.sub(r_ant, r_acad, oraciones_nuevas[idx], flags=re.IGNORECASE)

    texto_humanizado = " ".join(oraciones_nuevas).strip()
    analisis_final = analizar_texto_ia(texto_humanizado)

    p_antes = analisis_inicial["puntuacion_ia"]
    p_despues = analisis_final["puntuacion_ia"]
    reduccion = max(0, p_antes - p_despues)

    return {
        "texto_humanizado": texto_humanizado,
        "puntuacion_antes": p_antes,
        "puntuacion_despues": p_despues,
        "reduccion_porcentual": reduccion,
        "analisis_inicial": analisis_inicial,
        "analisis_final": analisis_final,
        "perfil_usuario": perfil_usuario,
        "modo_aplicado": modo,
        "nivel_aplicado": nivel,
    }
