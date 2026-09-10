"""
Editor de PDF.
Utiliza pypdf y PyMuPDF (fitz) para realizar operaciones sobre archivos PDF:
unir, dividir, comprimir, rotar, proteger, desbloquear, ordenar, firmar y traducir.
"""
from io import BytesIO
import zipfile
import base64
import re
import html
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader, PdfWriter, PdfMerger
import fitz  # PyMuPDF


def _traducir_bloque_individual(texto: str, idioma_destino: str = "es", idioma_origen: str = "auto") -> str:
    """Traduce un segmento de texto usando Google Translate con fallbacks a endpoint gtx y MyMemory."""
    if not texto or not texto.strip():
        return texto

    # 1. Google Translate Mobile endpoint con User-Agent móvil (evita bloqueo 500)
    try:
        url = "https://translate.google.com/m"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es,en;q=0.9",
        }
        params = {"sl": idioma_origen, "tl": idioma_destino, "q": texto}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            el = soup.find("div", {"class": "result-container"})
            if el:
                trad = html.unescape(el.get_text().strip())
                if trad and "Error 500" not in trad and "Please try again" not in trad:
                    return trad
    except Exception:
        pass

    # 2. Fallback: Google Translate client endpoint (gtx)
    try:
        url_gtx = "https://translate.googleapis.com/translate_a/single"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        params = {
            "client": "gtx",
            "sl": idioma_origen,
            "tl": idioma_destino,
            "dt": "t",
            "q": texto,
        }
        resp = requests.get(url_gtx, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            trad = "".join([part[0] for part in data[0] if part and part[0]]).strip()
            if trad:
                return html.unescape(trad)
    except Exception:
        pass

    # 3. Fallback: MyMemory API
    try:
        mapa_mm = {
            "es": "es-ES", "en": "en-US", "fr": "fr-FR",
            "de": "de-DE", "it": "it-IT", "pt": "pt-PT"
        }
        src = mapa_mm.get(idioma_origen, "autodetect")
        tgt = mapa_mm.get(idioma_destino, "es-ES")
        url_mm = "https://api.mymemory.translated.net/get"
        resp = requests.get(url_mm, params={"q": texto, "langpair": f"{src}|{tgt}"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            trad = data.get("responseData", {}).get("translatedText", "").strip()
            if trad and "MYMEMORY WARNING" not in trad:
                return html.unescape(trad)
    except Exception:
        pass

    return texto


def _traducir_parrafos(parrafos: list[str], idioma_destino: str, cache: dict) -> str:
    """Traduce un conjunto de párrafos por lotes para minimizar latencia y peticiones."""
    lotes = []
    lote_actual = []
    tamano_actual = 0
    for p in parrafos:
        if p in cache:
            continue
        # Evitar traducir cadenas sin letras (fórmulas, números, referencias)
        if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{2,}', p):
            cache[p] = p
            continue
        if tamano_actual + len(p) > 1200 and lote_actual:
            lotes.append(lote_actual)
            lote_actual = [p]
            tamano_actual = len(p)
        else:
            lote_actual.append(p)
            tamano_actual += len(p) + 2
    if lote_actual:
        lotes.append(lote_actual)

    for lote in lotes:
        texto_unido = '\n\n'.join(lote)
        traducido_unido = _traducir_bloque_individual(texto_unido, idioma_destino)
        partes = traducido_unido.split('\n\n')
        if len(partes) == len(lote):
            for orig, trad in zip(lote, partes):
                cache[orig] = trad.strip()
        else:
            for orig in lote:
                if orig not in cache:
                    cache[orig] = _traducir_bloque_individual(orig, idioma_destino)

    resultado = [cache.get(p, p) for p in parrafos]
    return '\n\n'.join(resultado)



def procesar_pdf(archivos_bytes: list[bytes], operacion: str, opciones: dict = None) -> bytes:
    """
    Procesa uno o más archivos PDF en bytes según la operación dada y devuelve el resultado en bytes.
    Soporta: 'unir', 'dividir', 'comprimir', 'rotar', 'proteger', 'desbloquear', 'ordenar', 'firmar', 'traducir'.
    """
    if opciones is None:
        opciones = {}

    if operacion == "unir":
        if not archivos_bytes:
            raise ValueError("No se proporcionaron archivos para unir.")
        fusor = PdfMerger()
        for pdf_bytes in archivos_bytes:
            fusor.append(BytesIO(pdf_bytes))
        
        buffer = BytesIO()
        fusor.write(buffer)
        fusor.close()
        return buffer.getvalue()

    if not archivos_bytes:
        raise ValueError("Se requiere al menos un archivo para esta operación.")
    
    bytes_entrada = archivos_bytes[0]

    if operacion == "proteger":
        clave = opciones.get("clave", "")
        if not clave:
            raise ValueError("Debes especificar una contraseña para proteger el PDF.")
        doc = fitz.open(stream=bytes_entrada, filetype="pdf")
        buffer = BytesIO()
        perm = fitz.PDF_PERM_ACCESSIBILITY | fitz.PDF_PERM_PRINT | fitz.PDF_PERM_COPY
        doc.save(
            buffer,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            user_pw=clave,
            owner_pw=clave,
            permissions=perm,
        )
        return buffer.getvalue()

    elif operacion == "desbloquear":
        clave = opciones.get("clave", "")
        doc = fitz.open(stream=bytes_entrada, filetype="pdf")
        if doc.is_encrypted:
            autenticado = doc.authenticate(clave)
            if not autenticado:
                raise ValueError("Contraseña incorrecta para desbloquear el PDF.")
        buffer = BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

    elif operacion == "ordenar":
        orden = opciones.get("orden", [])
        doc = fitz.open(stream=bytes_entrada, filetype="pdf")
        if not orden:
            raise ValueError("Debes especificar el nuevo orden de páginas.")
        doc_nuevo = fitz.open()
        for idx in orden:
            i = int(idx)
            if 0 <= i < len(doc):
                doc_nuevo.insert_pdf(doc, from_page=i, to_page=i)
        buffer = BytesIO()
        doc_nuevo.save(buffer)
        return buffer.getvalue()

    elif operacion == "firmar":
        texto_firma = opciones.get("texto_firma", "Firmado digitalmente")
        imagen_b64 = opciones.get("imagen_firma")
        doc = fitz.open(stream=bytes_entrada, filetype="pdf")

        for pagina in doc:
            rect = pagina.rect
            if imagen_b64:
                try:
                    datos_img = base64.b64decode(imagen_b64.split(",")[-1])
                    ancho_stamp = 150
                    alto_stamp = 50
                    rect_stamp = fitz.Rect(
                        rect.width - ancho_stamp - 20,
                        rect.height - alto_stamp - 20,
                        rect.width - 20,
                        rect.height - 20,
                    )
                    pagina.insert_image(rect_stamp, stream=datos_img)
                except Exception:
                    pass
            else:
                pagina.insert_text(
                    fitz.Point(rect.width - 220, rect.height - 30),
                    f"✍️ {texto_firma}",
                    fontsize=12,
                    color=(0, 0.2, 0.8),
                )
        buffer = BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

    elif operacion == "traducir":
        idioma_destino = opciones.get("idioma", "es")
        doc = fitz.open(stream=bytes_entrada, filetype="pdf")
        cache_traducciones = {}

        for pagina in doc:
            page_w = pagina.rect.width
            page_h = pagina.rect.height

            # 1. Detectar todos los obstáculos gráficos (imágenes raster y dibujos vectoriales)
            obstaculos = []
            for info in pagina.get_image_info(xrefs=True):
                r = fitz.Rect(info["bbox"])
                if r.width > 12 and r.height > 12:
                    obstaculos.append(r)
            for drw in pagina.get_drawings():
                r = fitz.Rect(drw["rect"])
                if r.width > 20 and r.height > 20:
                    obstaculos.append(r)

            # 2. Extraer bloques y determinar si la página usa layout de 2 o más columnas
            d = pagina.get_text("dict")
            blocks = d.get("blocks", [])

            anchos_validos = []
            for b in blocks:
                if b.get("type") == 0:
                    r = fitz.Rect(b["bbox"])
                    if r.width > 30 and r.height > 8:
                        anchos_validos.append(r.width)

            es_dos_columnas = False
            if len(anchos_validos) >= 3:
                angostos = sum(1 for w in anchos_validos if w < page_w * 0.48)
                if angostos / len(anchos_validos) >= 0.5:
                    es_dos_columnas = True

            # 3. Descomponer cada bloque en unidades homogéneas (evitar mezclar títulos con párrafos o puntos y aparte)
            unidades = []
            for b in blocks:
                if b.get("type") != 0:
                    continue
                lineas = b.get("lines", [])
                if not lineas:
                    continue

                segmentos = []
                seg_actual = []

                for l in lineas:
                    spans = l.get("spans", [])
                    txt_linea = "".join(s.get("text", "") for s in spans).strip()
                    if not txt_linea:
                        continue

                    l_chars = sum(len(s.get("text", "")) for s in spans)
                    b_chars = sum(len(s.get("text", "")) for s in spans if (s.get("flags", 0) & 16) or "bold" in s.get("font", "").lower() or "black" in s.get("font", "").lower())
                    it_chars = sum(len(s.get("text", "")) for s in spans if (s.get("flags", 0) & 2) or "italic" in s.get("font", "").lower() or "oblique" in s.get("font", "").lower())

                    es_bold = (b_chars / max(1, l_chars)) > 0.45
                    es_italic = (it_chars / max(1, l_chars)) > 0.45
                    avg_sz = sum(s.get("size", 10.0) * len(s.get("text", "")) for s in spans) / max(1, l_chars)

                    iniciar_nuevo = False
                    if seg_actual:
                        prev = seg_actual[-1]
                        # Cambio en estilo negrita (ej. Título en negrita seguido de texto normal)
                        if prev["bold"] != es_bold:
                            iniciar_nuevo = True
                        # Cambio notable en tamaño tipográfico
                        elif abs(prev["size"] - avg_sz) > 1.3:
                            iniciar_nuevo = True
                        else:
                            prev_txt = prev["text"].strip()
                            ends_punct = prev_txt.endswith((".", ":", "!", "?"))
                            gap_y = l["bbox"][1] - prev["bbox"][3]
                            line_h = prev["bbox"][3] - prev["bbox"][1]
                            is_indented = (l["bbox"][0] - prev["bbox"][0]) > 6.0
                            is_short = prev["bbox"][2] < (b["bbox"][2] - 18.0)

                            # Punto y aparte detectable
                            if ends_punct and (is_indented or is_short or gap_y > 1.35 * line_h):
                                iniciar_nuevo = True

                    if iniciar_nuevo and seg_actual:
                        segmentos.append(seg_actual)
                        seg_actual = []

                    seg_actual.append({
                        "line": l,
                        "text": txt_linea,
                        "bold": es_bold,
                        "italic": es_italic,
                        "size": avg_sz,
                        "bbox": fitz.Rect(l["bbox"]),
                        "spans": spans
                    })

                if seg_actual:
                    segmentos.append(seg_actual)

                for seg in segmentos:
                    texto_seg = ""
                    for item in seg:
                        ltxt = item["text"]
                        if texto_seg.endswith("-"):
                            texto_seg = texto_seg[:-1] + ltxt
                        elif texto_seg:
                            texto_seg += " " + ltxt
                        else:
                            texto_seg = ltxt
                    texto_seg = texto_seg.strip()
                    if not texto_seg:
                        continue

                    rect_seg = fitz.Rect(seg[0]["bbox"])
                    for item in seg[1:]:
                        rect_seg.include_rect(item["bbox"])

                    todos_spans = []
                    for item in seg:
                        todos_spans.extend(item["spans"])

                    total_chars = sum(len(s.get("text", "")) for s in todos_spans)
                    serif_score = 0
                    mono_score = 0
                    sans_score = 0
                    b_chars = 0
                    it_chars = 0
                    colores = []

                    for s in todos_spans:
                        c_len = len(s.get("text", ""))
                        fn_raw = s.get("font", "").lower()
                        flags = s.get("flags", 0)
                        if (flags & 16) or "bold" in fn_raw or "black" in fn_raw or "heavy" in fn_raw:
                            b_chars += c_len
                        if (flags & 2) or "italic" in fn_raw or "oblique" in fn_raw:
                            it_chars += c_len
                        colores.append(s.get("color", 0))

                        if any(kw in fn_raw for kw in ["times", "roman", "serif", "cambria", "georgia", "garamond", "minion", "palatino", "baskerville", "charter", "ptserif", "libertine", "stix", "cmr", "computermodern", "nimbusrom"]):
                            serif_score += c_len
                        elif any(kw in fn_raw for kw in ["courier", "mono", "consolas", "menlo", "sourcecode", "typewriter", "fixed"]):
                            mono_score += c_len
                        else:
                            sans_score += c_len

                    es_bold = (b_chars / max(1, total_chars)) > 0.45
                    es_italic = (it_chars / max(1, total_chars)) > 0.45

                    if serif_score >= sans_score and serif_score >= mono_score:
                        fn = "tibi" if (es_bold and es_italic) else ("tibo" if es_bold else ("tiit" if es_italic else "tiro"))
                    elif mono_score >= sans_score:
                        fn = "cobi" if (es_bold and es_italic) else ("cobo" if es_bold else ("coit" if es_italic else "cour"))
                    else:
                        fn = "hebi" if (es_bold and es_italic) else ("hebo" if es_bold else ("heit" if es_italic else "helv"))

                    avg_size = sum(s.get("size", 10.0) * len(s.get("text", "")) for s in todos_spans) / max(1, total_chars)
                    c_int = colores[0] if colores else 0
                    r_col = ((c_int >> 16) & 255) / 255.0
                    g_col = ((c_int >> 8) & 255) / 255.0
                    b_col = (c_int & 255) / 255.0

                    es_tit = (es_bold and rect_seg.height < 28.0) or avg_size > 12.5 or (len(texto_seg) < 60 and bool(re.match(r'^(I|II|III|IV|V|VI|VII|VIII|IX|X|\d+|[A-Z])\.\s+', texto_seg)))

                    unidades.append({
                        "orig_rect": rect_seg,
                        "texto": texto_seg,
                        "fontname": fn,
                        "size": avg_size,
                        "color": (r_col, g_col, b_col),
                        "bold": es_bold,
                        "italic": es_italic,
                        "es_titulo": es_tit,
                        "es_dos_columnas": es_dos_columnas
                    })

            if not unidades:
                continue

            # 4. Traducir textos pendientes
            textos_a_traducir = []
            for u in unidades:
                t = u["texto"]
                if t not in cache_traducciones:
                    if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{2,}', t):
                        cache_traducciones[t] = t
                    else:
                        textos_a_traducir.append(t)

            if textos_a_traducir:
                _traducir_parrafos(textos_a_traducir, idioma_destino, cache_traducciones)

            # 5. Redactar el texto original con fill=None para no alterar imágenes ni fondos
            for u in unidades:
                pagina.add_redact_annot(u["orig_rect"], fill=None)
            pagina.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

            # 6. Insertar texto traducido con delimitación estricta anti-colisión y anti-traspaso
            for i, u in enumerate(unidades):
                orig_r = u["orig_rect"]
                trad = cache_traducciones.get(u["texto"], u["texto"])
                fn = u["fontname"]
                orig_sz = u["size"]
                col = u["color"]
                es_tit = u["es_titulo"]
                es_dos_col = u["es_dos_columnas"]

                mid_x = (orig_r.x0 + orig_r.x1) / 2
                es_centrado = abs(mid_x - page_w / 2) < 30 and orig_r.width > page_w * 0.35

                # --- Límites horizontales ---
                if es_centrado:
                    margin = min(orig_r.x0, page_w - orig_r.x1)
                    tx0 = max(36.0, margin - 15.0)
                    tx1 = min(page_w - 36.0, page_w - tx0)
                    align = fitz.TEXT_ALIGN_CENTER
                else:
                    tx0 = orig_r.x0
                    align = fitz.TEXT_ALIGN_LEFT
                    if es_dos_col:
                        if orig_r.x1 <= page_w * 0.52:
                            # Columna izquierda: NUNCA traspasa el gutter central
                            tx1 = min(page_w * 0.485, max(orig_r.x1 + 4.0, orig_r.x0 + 60.0))
                        elif orig_r.x0 >= page_w * 0.48:
                            # Columna derecha
                            tx1 = min(page_w - 36.0, max(orig_r.x1 + 4.0, orig_r.x0 + 60.0))
                        else:
                            # Abarca ambas columnas
                            tx1 = min(page_w - 36.0, orig_r.x1 + 10.0)
                    else:
                        tx1 = min(page_w - 36.0, orig_r.x1 + 8.0)

                # Recorte por obstáculos a la derecha (evitar tapar imágenes o figuras)
                for obs in obstaculos:
                    v_overlap = max(orig_r.y0, obs.y0) < min(orig_r.y1, obs.y1)
                    if v_overlap and obs.x0 >= orig_r.x0:
                        tx1 = min(tx1, obs.x0 - 8.0)

                # --- Límites verticales ---
                next_y0 = page_h - 25.0
                for j, other in enumerate(unidades):
                    if i == j:
                        continue
                    o_r = other["orig_rect"]
                    if o_r.y0 >= orig_r.y0 + 2.0:
                        h_overlap = max(tx0, o_r.x0) < min(tx1, o_r.x1) + 10.0
                        if es_centrado or h_overlap:
                            if o_r.y0 < next_y0:
                                next_y0 = o_r.y0

                for obs in obstaculos:
                    if obs.y0 >= orig_r.y0 + 2.0:
                        h_overlap = max(tx0, obs.x0) < min(tx1, obs.x1) + 10.0
                        if h_overlap and obs.y0 < next_y0:
                            next_y0 = obs.y0

                if es_tit:
                    # Títulos: altura estricta para jamás invadir el texto de abajo
                    ty1 = max(orig_r.y1, min(orig_r.y1 + 4.0, next_y0 - 2.0))
                else:
                    ty1 = max(orig_r.y1, next_y0 - 2.0)

                target_rect = fitz.Rect(tx0, orig_r.y0, max(tx0 + 20.0, tx1), max(orig_r.y0 + 8.0, ty1))

                # Auto-ajuste de tamaño tipográfico para encajar perfectamente
                curr_size = orig_sz
                min_sz = max(4.5, orig_sz * 0.65)
                escrito = False
                while curr_size >= min_sz:
                    rc = pagina.insert_textbox(target_rect, trad, fontsize=curr_size, color=col, fontname=fn, align=align)
                    if rc >= 0:
                        escrito = True
                        break
                    curr_size -= 0.25

                if not escrito:
                    while curr_size >= 4.0:
                        rc = pagina.insert_textbox(target_rect, trad, fontsize=curr_size, color=col, fontname=fn, align=align)
                        if rc >= 0:
                            escrito = True
                            break
                        curr_size -= 0.25

                if not escrito:
                    pagina.insert_textbox(target_rect, trad, fontsize=4.0, color=col, fontname=fn, align=align)

        buffer = BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

    lector = PdfReader(BytesIO(bytes_entrada))
    escritor = PdfWriter()

    if operacion == "dividir":
        desde = opciones.get("desde")
        hasta = opciones.get("hasta")
        if desde is not None or hasta is not None:
            val_desde = int(desde) if desde is not None else 1
            val_hasta = int(hasta) if hasta is not None else len(lector.pages)
            
            inicio = max(0, val_desde - 1)
            fin = min(len(lector.pages), val_hasta)
            
            for i in range(inicio, fin):
                escritor.add_page(lector.pages[i])
                
            buffer = BytesIO()
            escritor.write(buffer)
            return buffer.getvalue()
        else:
            buffer_zip = BytesIO()
            with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
                for i, pagina in enumerate(lector.pages):
                    escritor_temp = PdfWriter()
                    escritor_temp.add_page(pagina)
                    buffer_temp = BytesIO()
                    escritor_temp.write(buffer_temp)
                    archivo_zip.writestr(f"pagina_{i+1}.pdf", buffer_temp.getvalue())
            return buffer_zip.getvalue()

    elif operacion == "comprimir":
        for pagina in lector.pages:
            pagina.compress_content_streams()
            escritor.add_page(pagina)
        buffer = BytesIO()
        escritor.write(buffer)
        return buffer.getvalue()

    elif operacion == "rotar":
        grados = int(opciones.get("grados", 90))
        for pagina in lector.pages:
            pagina.rotate(grados)
            escritor.add_page(pagina)
        buffer = BytesIO()
        escritor.write(buffer)
        return buffer.getvalue()

    else:
        raise ValueError(f"Operación PDF no soportada: {operacion}")

