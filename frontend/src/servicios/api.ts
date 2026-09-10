import axios from 'axios';

const URL_BASE = import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? '/api' : 'https://filemaster.onrender.com/api');

const cliente = axios.create({
  baseURL: URL_BASE,
  timeout: 600000, // 10 minutos para soportar transferencia de archivos de hasta 1GB
});

export async function convertirArchivo(
  archivo: File,
  formatoSalida: string,
  alProgreso?: (progreso: number) => void,
): Promise<Blob> {
  const datosFormulario = new FormData();
  datosFormulario.append('archivo', archivo);
  datosFormulario.append('formato_salida', formatoSalida);

  const respuesta = await cliente.post('/convertir', datosFormulario, {
    responseType: 'blob',
    onUploadProgress: (evento) => {
      if (evento.total && alProgreso) {
        const progreso = Math.round((evento.loaded * 100) / evento.total);
        alProgreso(progreso);
      }
    },
  });

  return respuesta.data;
}

export async function comprimirImagen(
  archivo: File,
  calidad: number = 80,
  alProgreso?: (progreso: number) => void,
): Promise<Blob> {
  const datosFormulario = new FormData();
  datosFormulario.append('archivo', archivo);
  datosFormulario.append('calidad', calidad.toString());

  const respuesta = await cliente.post('/comprimir', datosFormulario, {
    responseType: 'blob',
    onUploadProgress: (evento) => {
      if (evento.total && alProgreso) {
        alProgreso(Math.round((evento.loaded * 100) / evento.total));
      }
    },
  });

  return respuesta.data;
}



export async function generarQR(
  contenido: string,
  tamano: number = 300,
  color: string = '#000000',
  fondo: string = '#FFFFFF',
): Promise<Blob> {
  const respuesta = await cliente.post('/generar-qr', {
    contenido,
    tamano,
    color,
    fondo,
  }, { responseType: 'blob' });

  return respuesta.data;
}

export async function textoAVoz(
  texto: string,
  voz: string = 'es-MX-DaliaNeural',
  velocidad: number = 1.0,
): Promise<Blob> {
  const respuesta = await cliente.post('/texto-a-voz', {
    texto,
    voz,
    velocidad,
  }, { responseType: 'blob' });

  return respuesta.data;
}



export async function editarPDF(
  archivos: File[],
  operacion: string,
  opciones?: Record<string, unknown>,
  alProgreso?: (progreso: number) => void,
): Promise<Blob> {
  const datosFormulario = new FormData();
  archivos.forEach((archivo) => datosFormulario.append('archivos', archivo));
  datosFormulario.append('operacion', operacion);
  if (opciones) {
    datosFormulario.append('opciones', JSON.stringify(opciones));
  }

  const respuesta = await cliente.post('/editar-pdf', datosFormulario, {
    responseType: 'blob',
    onUploadProgress: (evento) => {
      if (evento.total && alProgreso) {
        alProgreso(Math.round((evento.loaded * 100) / evento.total));
      }
    },
  });

  return respuesta.data;
}

export function descargarBlob(blob: Blob, nombreArchivo: string): void {
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = nombreArchivo;
  document.body.appendChild(enlace);
  enlace.click();
  document.body.removeChild(enlace);

  setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 250);
}

/* === Tipos y funciones para Detector y Humanizador IA === */

export interface OracionAnalizada {
  id: number;
  texto: string;
  puntuacion_ia: number;
  nivel: 'humano' | 'mixto' | 'ia';
  cliches: string[];
  palabras: number;
}

export interface MetricasIA {
  longitud_media_oraciones: number;
  desviacion_ritmo: number;
  total_palabras: number;
  cliches_detectados: number;
  riqueza_lexica_pct: number;
}

export interface ResultadoAnalisisIA {
  puntuacion_ia: number;
  etiqueta: string;
  color: string;
  resumen: string;
  metricas: MetricasIA;
  cliches: string[];
  oraciones: OracionAnalizada[];
}

export interface PerfilEstiloUsuario {
  valido: boolean;
  mensaje?: string;
  longitud_media?: number;
  desviacion?: number;
  persona?: string;
  tono_persona?: string;
  icono_persona?: string;
  registro?: string;
  etiqueta_registro?: string;
  puntuacion?: {
    usa_preguntas: boolean;
    usa_exclamaciones: boolean;
    usa_puntos_suspensivos: boolean;
    usa_guiones: boolean;
  };
  conectores_detectados?: string[];
  resumen_estilo?: string;
}

export interface ResultadoHumanizacion {
  texto_humanizado: string;
  puntuacion_antes: number;
  puntuacion_despues: number;
  reduccion_porcentual: number;
  analisis_inicial: ResultadoAnalisisIA;
  analisis_final: ResultadoAnalisisIA;
  perfil_usuario?: PerfilEstiloUsuario | null;
  modo_aplicado: string;
  nivel_aplicado: string;
}

export async function analizarTextoIA(texto: string): Promise<ResultadoAnalisisIA> {
  const respuesta = await cliente.post<ResultadoAnalisisIA>('/detector-ia/analizar', { texto });
  return respuesta.data;
}

export async function humanizarTexto(
  texto: string,
  modo: 'automatico' | 'estilo_personal' = 'automatico',
  nivel: 'casual' | 'equilibrado' | 'academico' = 'equilibrado',
  textoMuestraUsuario?: string
): Promise<ResultadoHumanizacion> {
  const respuesta = await cliente.post<ResultadoHumanizacion>('/detector-ia/humanizar', {
    texto,
    modo,
    nivel,
    texto_muestra_usuario: textoMuestraUsuario || '',
  });
  return respuesta.data;
}

export async function analizarEstiloUsuario(textoMuestra: string): Promise<PerfilEstiloUsuario> {
  const respuesta = await cliente.post<PerfilEstiloUsuario>('/detector-ia/analizar-estilo', {
    texto_muestra: textoMuestra,
  });
  return respuesta.data;
}

