
export function formatearTamano(bytes: number): string {
  if (bytes === 0) return '0 B';

  const unidades = ['B', 'KB', 'MB', 'GB'];
  const indice = Math.floor(Math.log(bytes) / Math.log(1024));
  const tamano = bytes / Math.pow(1024, indice);

  return `${tamano.toFixed(indice === 0 ? 0 : 1)} ${unidades[indice]}`;
}

export function formatearFecha(fechaISO: string): string {
  const fecha = new Date(fechaISO);
  return fecha.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function generarId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

export function obtenerExtension(nombreArchivo: string): string {
  const partes = nombreArchivo.split('.');
  return partes.length > 1 ? partes.pop()!.toLowerCase() : '';
}

export function truncarNombre(nombre: string, maxLongitud: number = 25): string {
  if (nombre.length <= maxLongitud) return nombre;

  const extension = obtenerExtension(nombre);
  const nombreBase = nombre.slice(0, nombre.lastIndexOf('.'));
  const longitudBase = maxLongitud - extension.length - 4; 

  return `${nombreBase.slice(0, longitudBase)}...${extension}`;
}
