
const TAMANO_MAXIMO = 1024 * 1024 * 1024; // 1 GB

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
      mensaje: `El archivo excede el tamaño máximo de 1GB (${(archivo.size / 1024 / 1024).toFixed(1)}MB)`,
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

export interface ResultadoValidacionClave {
  valido: boolean;
  mensaje?: string;
  puntuacion: number; // 0 a 3
  etiqueta: 'Débil' | 'Aceptable' | 'Segura';
  color: string;
}

export function validarContrasena(clave: string): ResultadoValidacionClave {
  if (!clave || !clave.trim()) {
    return {
      valido: false,
      mensaje: 'La contraseña es requerida.',
      puntuacion: 0,
      etiqueta: 'Débil',
      color: '#EF4444',
    };
  }

  if (clave.length < 8) {
    return {
      valido: false,
      mensaje: `La contraseña debe tener al menos 8 caracteres (actual: ${clave.length}).`,
      puntuacion: 1,
      etiqueta: 'Débil',
      color: '#EF4444',
    };
  }

  if (clave.length > 128) {
    return {
      valido: false,
      mensaje: 'La contraseña excede el límite máximo de 128 caracteres.',
      puntuacion: 1,
      etiqueta: 'Débil',
      color: '#EF4444',
    };
  }

  const tieneLetra = /[a-zA-ZáéíóúÁÉÍÓÚñÑ]/.test(clave);
  const tieneNumeroOSimbolo = /[\d\W_]/.test(clave);

  if (!tieneLetra || !tieneNumeroOSimbolo) {
    return {
      valido: false,
      mensaje: 'La contraseña debe combinar letras con al menos un número o símbolo especial.',
      puntuacion: 1,
      etiqueta: 'Débil',
      color: '#F59E0B',
    };
  }

  const tieneMayuscula = /[A-ZÁÉÍÓÚÑ]/.test(clave);
  const tieneMinuscula = /[a-záéíóúñ]/.test(clave);
  const tieneNumero = /\d/.test(clave);
  const tieneSimbolo = /[\W_]/.test(clave);

  const esRobusta = clave.length >= 10 && tieneMayuscula && tieneMinuscula && (tieneNumero && tieneSimbolo);

  if (esRobusta) {
    return {
      valido: true,
      puntuacion: 3,
      etiqueta: 'Segura',
      color: '#10B981',
    };
  }

  return {
    valido: true,
    puntuacion: 2,
    etiqueta: 'Aceptable',
    color: '#3B82F6',
  };
}

export async function extraerMensajeError(err: unknown, fallback: string): Promise<string> {
  try {
    const error = err as { response?: { data?: unknown; status?: number } };
    if (!error.response) return fallback;

    const data = error.response.data;
    if (data instanceof Blob) {
      const texto = await data.text();
      try {
        const json = JSON.parse(texto);
        return json.detalle || json.detail || fallback;
      } catch {
        return texto || fallback;
      }
    }

    if (typeof data === 'object' && data !== null) {
      const d = data as { detalle?: string; detail?: string };
      return d.detalle || d.detail || fallback;
    }
  } catch {
    // Si falla el parseo, usar mensaje por defecto
  }
  return fallback;
}
