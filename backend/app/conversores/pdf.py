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


def _agrupar_lineas_inteligente(texto_crudo: str) -> list[str]:
    """Une líneas del PDF en párrafos coherentes manteniendo encabezados y listas separadas."""
    texto = re.sub(r'(\w+)-\n(\w+)', r'\1\2', texto_crudo)
    lineas = [l.strip() for l in texto.split('\n')]
    parrafos = []
    actual = ''
    for l in lineas:
        if not l:
            if actual:
                parrafos.append(actual)
                actual = ''
            continue
        if not actual:
            actual = l
            continue
        es_posible_titulo = len(actual) < 45 and not actual.endswith((',', ';', '-'))
        es_lista = l.startswith(('-', '*', '•', '·', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.'))
        if es_posible_titulo or es_lista:
            parrafos.append(actual)
            actual = l
        else:
            actual += ' ' + l
    if actual:
        parrafos.append(actual)
    return parrafos


def _traducir_parrafos(parrafos: list[str], idioma_destino: str, cache: dict) -> str:
    """Traduce un conjunto de párrafos por lotes para minimizar latencia y peticiones."""
    lotes = []
    lote_actual = []
    tamano_actual = 0
    for p in parrafos:
        if p in cache:
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


def _renderizar_texto_en_documento(doc_salida: fitz.Document, texto_traducido: str, ancho: float = 595, alto: float = 842):
    """
    Inserta el texto traducido en el documento PDF asegurando que NUNCA quede una página en blanco.
    Si no cabe en una página reduciendo fuente, lo distribuye en páginas consecutivas.
    """
    margen_x = 40
    margen_y = 45
    rect = fitz.Rect(margen_x, margen_y, ancho - margen_x, alto - margen_y)

    # 1. Intentar ajustar en 1 sola página reduciendo dinámicamente el tamaño de fuente
    pagina = doc_salida.new_page(width=ancho, height=alto)
    ajustado = False
    for sz in [11.0, 10.5, 10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0]:
        rc = pagina.insert_textbox(rect, texto_traducido, fontsize=sz, fontname="helv")
        if rc >= 0:
            ajustado = True
            break

    if ajustado:
        return

    # 2. Si excede una página incluso con fuente reducida, fluir a través de páginas consecutivas
    doc_salida.delete_page(-1)
    parrafos = [p for p in texto_traducido.split('\n\n') if p.strip()]
    pagina_actual = doc_salida.new_page(width=ancho, height=alto)
    acumulado = ''
    tam_fuente = 9.0

    for p in parrafos:
        candidato = (acumulado + '\n\n' + p).strip() if acumulado else p
        doc_temp = fitz.open()
        p_temp = doc_temp.new_page(width=ancho, height=alto)
        rc = p_temp.insert_textbox(rect, candidato, fontsize=tam_fuente, fontname="helv")
        doc_temp.close()

        if rc >= 0:
            acumulado = candidato
        else:
            if acumulado:
                pagina_actual.insert_textbox(rect, acumulado, fontsize=tam_fuente, fontname="helv")
                pagina_actual = doc_salida.new_page(width=ancho, height=alto)
                acumulado = p
            else:
                oraciones = p.split('. ')
                sub_acum = ''
                for s in oraciones:
                    s_c = (sub_acum + '. ' + s).strip() if sub_acum else s
                    doc_temp = fitz.open()
                    p_temp = doc_temp.new_page(width=ancho, height=alto)
                    rc_s = p_temp.insert_textbox(rect, s_c, fontsize=tam_fuente, fontname="helv")
                    doc_temp.close()
                    if rc_s >= 0:
                        sub_acum = s_c
                    else:
                        pagina_actual.insert_textbox(rect, sub_acum, fontsize=tam_fuente, fontname="helv")
                        pagina_actual = doc_salida.new_page(width=ancho, height=alto)
                        sub_acum = s
                acumulado = sub_acum

    if acumulado:
        pagina_actual.insert_textbox(rect, acumulado, fontsize=tam_fuente, fontname="helv")


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
            d = pagina.get_text("dict")
            blocks = d.get("blocks", [])
            blocks_a_reemplazar = []

            for b in blocks:
                if b.get("type") == 0:  # Bloque de texto
                    lines_text = []
                    sizes = []
                    colors = []
                    for line in b.get("lines", []):
                        spans = line.get("spans", [])
                        line_str = "".join([s.get("text", "") for s in spans]).strip()
                        if line_str:
                            lines_text.append(line_str)
                            for s in spans:
                                sizes.append(s.get("size", 11.0))
                                colors.append(s.get("color", 0))

                    if not lines_text:
                        continue

                    # Unir líneas respetando palabras cortadas con guión
                    orig_text = ""
                    for linea in lines_text:
                        if orig_text.endswith("-"):
                            orig_text = orig_text[:-1] + linea
                        elif orig_text:
                            orig_text += " " + linea
                        else:
                            orig_text = linea
                    orig_text = orig_text.strip()

                    if not orig_text:
                        continue

                    avg_size = sum(sizes) / len(sizes) if sizes else 11.0
                    c_int = colors[0] if colors else 0
                    r = ((c_int >> 16) & 255) / 255.0
                    g = ((c_int >> 8) & 255) / 255.0
                    b_col = (c_int & 255) / 255.0

                    rect = fitz.Rect(b["bbox"])
                    blocks_a_reemplazar.append({
                        "rect": rect,
                        "orig": orig_text,
                        "size": avg_size,
                        "color": (r, g, b_col),
                    })

            if not blocks_a_reemplazar:
                # Página sin bloques de texto (imagen pura, escaneo, etc.): se mantiene intacta
                continue

            # Traducir los textos de los bloques (por lotes para velocidad)
            textos_pendientes = [item["orig"] for item in blocks_a_reemplazar if item["orig"] not in cache_traducciones]
            if textos_pendientes:
                _traducir_parrafos(textos_pendientes, idioma_destino, cache_traducciones)

            # 1. Redactar el texto original con fill=None para no alterar el fondo ni gráficos
            for item in blocks_a_reemplazar:
                pagina.add_redact_annot(item["rect"], fill=None)

            pagina.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

            # 2. Insertar el texto traducido en la posición exacta del bloque original
            for item in blocks_a_reemplazar:
                rect = item["rect"]
                trad = cache_traducciones.get(item["orig"], item["orig"])
                col = item["color"]
                orig_size = item["size"]

                # Holgura de margen para permitir el flujo natural del texto traducido
                target_rect = fitz.Rect(
                    rect.x0,
                    rect.y0,
                    min(pagina.rect.width - 15, max(rect.x1 + 15, rect.x0 + 60)),
                    min(pagina.rect.height - 15, rect.y1 + 25)
                )

                curr_size = orig_size
                escrito = False
                while curr_size >= 6.0:
                    rc = pagina.insert_textbox(target_rect, trad, fontsize=curr_size, color=col, fontname="helv")
                    if rc >= 0:
                        escrito = True
                        break
                    curr_size -= 0.5

                if not escrito:
                    # Si no cupo, extender hacia abajo el área disponible
                    target_rect.y1 = min(pagina.rect.height - 10, target_rect.y1 + 45)
                    pagina.insert_textbox(target_rect, trad, fontsize=6.5, color=col, fontname="helv")

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

