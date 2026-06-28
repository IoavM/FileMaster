
const TAMANO_MAXIMO = 50 * 1024 * 1024;

const TIPOS_PERMITIDOS: Record<string, string[]> = {
  documento: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'text/csv',
  ],
  imagen: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/svg+xml',
    'image/bmp',
    'image/tiff',
  ],
  audio: [
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
    'audio/flac',
    'audio/aac',
    'audio/mp4',
  ],
  video: [
    'video/mp4',
    'video/avi',
    'video/quicktime',
    'video/webm',
    'video/x-matroska',
  ],
};

const TODOS_LOS_TIPOS = Object.values(TIPOS_PERMITIDOS).flat();

export function validarTamano(archivo: File): { valido: boolean; mensaje?: string } {
  if (archivo.size > TAMANO_MAXIMO) {
    return {
      valido: false,
      mensaje: `El archivo excede el tamaño máximo de 50MB (${(archivo.size / 1024 / 1024).toFixed(1)}MB)`,
    };
  }
  return { valido: true };
}

export function validarTipo(archivo: File): { valido: boolean; mensaje?: string } {
  if (!TODOS_LOS_TIPOS.includes(archivo.type)) {
    return {
      valido: false,
      mensaje: `Tipo de archivo no soportado: ${archivo.type || 'desconocido'}`,
    };
  }
  return { valido: true };
}

export function validarArchivo(archivo: File): { valido: boolean; mensaje?: string } {
  const resultadoTamano = validarTamano(archivo);
  if (!resultadoTamano.valido) return resultadoTamano;

  const resultadoTipo = validarTipo(archivo);
  if (!resultadoTipo.valido) return resultadoTipo;

  return { valido: true };
}

export function obtenerCategoria(tipoMime: string): string {
  for (const [categoria, tipos] of Object.entries(TIPOS_PERMITIDOS)) {
    if (tipos.includes(tipoMime)) return categoria;
  }
  return 'desconocido';
}
