import axios from 'axios';

const URL_BASE = import.meta.env.VITE_API_URL || '/api';

const cliente = axios.create({
  baseURL: URL_BASE,
  timeout: 120000, 
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

export async function eliminarFondo(
  archivo: File,
  alProgreso?: (progreso: number) => void,
): Promise<Blob> {
  const datosFormulario = new FormData();
  datosFormulario.append('archivo', archivo);

  const respuesta = await cliente.post('/eliminar-fondo', datosFormulario, {
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

export async function descargarYouTube(
  url: string,
  formato: 'mp4' | 'mp3' = 'mp4',
  calidad: string = 'best',
): Promise<Blob> {
  const respuesta = await cliente.post('/descargar-youtube', {
    url,
    formato,
    calidad,
  }, {
    responseType: 'blob',
    timeout: 300000, 
  });

  return respuesta.data;
}

export async function editarPDF(
  archivos: File[],
  operacion: 'unir' | 'dividir' | 'comprimir' | 'rotar',
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
