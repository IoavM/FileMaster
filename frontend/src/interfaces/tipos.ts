/* === Tipos para la aplicación FileMaster === */

/** Estados posibles de una conversión */
export type EstadoConversion = 'pendiente' | 'subiendo' | 'convirtiendo' | 'completado' | 'error';

/** Formatos de archivo soportados */
export type FormatoArchivo =
  | 'pdf' | 'docx' | 'xlsx' | 'pptx' | 'txt' | 'csv'
  | 'jpg' | 'jpeg' | 'png' | 'gif' | 'webp' | 'svg' | 'bmp' | 'tiff'
  | 'mp3' | 'wav' | 'ogg' | 'flac' | 'aac'
  | 'mp4' | 'avi' | 'mov' | 'webm' | 'mkv';

/** Categoría de herramienta */
export type CategoriaHerramienta =
  | 'conversion'
  | 'pdf'
  | 'imagen'
  | 'audio'
  | 'video'
  | 'utilidad';

/** Archivo subido por el usuario */
export interface ArchivoSubido {
  id: string;
  nombre: string;
  tamano: number;
  tipo: string;
  archivo: File;
  progreso: number;
  estado: EstadoConversion;
  formatoSalida?: string;
  urlDescarga?: string;
  error?: string;
}

/** Conversión reciente para el historial */
export interface ConversionReciente {
  id: string;
  nombreArchivo: string;
  formatoEntrada: string;
  formatoSalida: string;
  tamano: string;
  estado: EstadoConversion;
  fecha: string;
  urlDescarga?: string;
}

/** Atajo rápido */
export interface AtajoRapido {
  id: string;
  titulo: string;
  icono: string;
  colorIcono: string;
  ruta: string;
}

/** Herramienta disponible */
export interface Herramienta {
  id: string;
  titulo: string;
  descripcion: string;
  icono: string;
  categoria: CategoriaHerramienta;
  ruta: string;
  color: string;
}

/** Props genéricas de variante de botón */
export type VarianteBoton = 'primario' | 'secundario' | 'invertido' | 'contorno';

/** Formato de conversión con su categoría */
export interface OpcionFormato {
  valor: FormatoArchivo;
  etiqueta: string;
  categoria: 'documento' | 'imagen' | 'audio' | 'video';
}
