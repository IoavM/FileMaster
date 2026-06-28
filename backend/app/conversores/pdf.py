"""
Editor de PDF.
Utiliza pypdf para realizar operaciones sobre archivos PDF como unir, dividir, comprimir y rotar.
"""
from io import BytesIO
import zipfile
from pypdf import PdfReader, PdfWriter, PdfMerger

def procesar_pdf(archivos_bytes: list[bytes], operacion: str, opciones: dict = None) -> bytes:
    """
    Procesa uno o más archivos PDF en bytes según la operación dada y devuelve el resultado en bytes.
    Soporta: 'unir', 'dividir', 'comprimir', 'rotar'.
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
    lector = PdfReader(BytesIO(bytes_entrada))
    escritor = PdfWriter()

    if operacion == "dividir":
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
