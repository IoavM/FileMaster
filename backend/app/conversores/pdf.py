"""
Editor de PDF.
Utiliza pypdf y PyMuPDF (fitz) para realizar operaciones sobre archivos PDF:
unir, dividir, comprimir, rotar, proteger, desbloquear, ordenar, firmar y traducir.
"""
from io import BytesIO
import zipfile
import base64
from pypdf import PdfReader, PdfWriter, PdfMerger
import fitz  # PyMuPDF
from deep_translator import GoogleTranslator

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
        traductor = GoogleTranslator(source="auto", target=idioma_destino)
        doc = fitz.open(stream=bytes_entrada, filetype="pdf")
        doc_traducido = fitz.open()

        for pagina in doc:
            texto = pagina.get_text()
            rect = pagina.rect
            nueva_pag = doc_traducido.new_page(width=rect.width, height=rect.height)
            if texto.strip():
                try:
                    texto_trad = traductor.translate(texto)
                except Exception:
                    texto_trad = texto
                nueva_pag.insert_textbox(
                    fitz.Rect(20, 20, rect.width - 20, rect.height - 20),
                    texto_trad,
                    fontsize=11,
                )
        buffer = BytesIO()
        doc_traducido.save(buffer)
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

