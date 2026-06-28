# Imagen base oficial de Python
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y habilitar buffering de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para multimedia y procesamiento de imágenes
# ffmpeg: Requerido por pydub, yt-dlp
# libgl1-mesa-glx, libglib2.0-0: Requeridos por OpenCV / rembg
RUN for i in 1 2 3; do \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            ffmpeg \
            libglib2.0-0 \
            libgl1-mesa-glx \
            build-essential && \
        break || (echo "Intento $i fallido. Reintentando..." && sleep 5); \
    done \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-descargar el modelo de rembg (u2net) durante la construcción de la imagen
# Esto evita que el servidor intente descargarlo al iniciar y cause un timeout de puerto en Render
RUN python -c "import rembg; rembg.new_session('u2net')"

# Copiar el código del backend
COPY . .

# Exponer el puerto por el que escuchará FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación usando uvicorn, enlazando al puerto dinámico de Render
CMD ["sh", "-c", "uvicorn app.principal:app --host 0.0.0.0 --port ${PORT:-8000}"]
