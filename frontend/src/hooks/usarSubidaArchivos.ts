import { useState, useCallback, useRef } from 'react';
import type { ArchivoSubido, EstadoConversion } from '../interfaces/tipos';
import { validarArchivo } from '../utilidades/validadores';
import { generarId, obtenerExtension } from '../utilidades/formateadores';

export function usarSubidaArchivos() {
  const [archivos, establecerArchivos] = useState<ArchivoSubido[]>([]);
  const [arrastrando, establecerArrastrando] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const procesarArchivos = useCallback((listaArchivos: FileList | null) => {
    if (!listaArchivos) return;

    const nuevosArchivos: ArchivoSubido[] = [];

    Array.from(listaArchivos).forEach((archivo) => {
      const validacion = validarArchivo(archivo);

      nuevosArchivos.push({
        id: generarId(),
        nombre: archivo.name,
        tamano: archivo.size,
        tipo: archivo.type,
        archivo,
        progreso: 0,
        estado: validacion.valido ? 'pendiente' : 'error',
        error: validacion.mensaje,
      });
    });

    establecerArchivos((prev) => [...prev, ...nuevosArchivos]);
  }, []);

  const alArrastrarSobre = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    establecerArrastrando(true);
  }, []);

  const alSalirDelArea = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    establecerArrastrando(false);
  }, []);

  const alSoltar = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    establecerArrastrando(false);
    procesarArchivos(e.dataTransfer.files);
  }, [procesarArchivos]);

  const abrirSelector = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const alSeleccionar = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    procesarArchivos(e.target.files);
    if (inputRef.current) inputRef.current.value = '';
  }, [procesarArchivos]);

  const actualizarArchivo = useCallback((id: string, cambios: Partial<ArchivoSubido>) => {
    establecerArchivos((prev) =>
      prev.map((a) => (a.id === id ? { ...a, ...cambios } : a))
    );
  }, []);

  const establecerFormatoSalida = useCallback((id: string, formato: string) => {
    actualizarArchivo(id, { formatoSalida: formato });
  }, [actualizarArchivo]);

  const actualizarProgreso = useCallback((id: string, progreso: number, estado?: EstadoConversion) => {
    const cambios: Partial<ArchivoSubido> = { progreso };
    if (estado) cambios.estado = estado;
    actualizarArchivo(id, cambios);
  }, [actualizarArchivo]);

  const eliminarArchivo = useCallback((id: string) => {
    establecerArchivos((prev) => prev.filter((a) => a.id !== id));
  }, []);

  const limpiarArchivos = useCallback(() => {
    establecerArchivos([]);
  }, []);

  const obtenerFormatosDisponibles = useCallback((nombreArchivo: string): string[] => {
    const ext = obtenerExtension(nombreArchivo).toLowerCase();

    const mapaFormatos: Record<string, string[]> = {
      
      pdf: ['docx', 'txt', 'jpg', 'png'],
      docx: ['pdf', 'txt'],
      doc: ['pdf', 'docx', 'txt'],
      xlsx: ['pdf', 'csv'],
      xls: ['pdf', 'xlsx', 'csv'],
      pptx: ['pdf'],
      txt: ['pdf', 'docx'],
      csv: ['xlsx', 'pdf'],
      
      jpg: ['png', 'webp', 'pdf', 'bmp'],
      jpeg: ['png', 'webp', 'pdf', 'bmp'],
      png: ['jpg', 'webp', 'pdf', 'bmp'],
      webp: ['jpg', 'png', 'pdf'],
      bmp: ['jpg', 'png', 'webp'],
      gif: ['jpg', 'png', 'webp'],
      tiff: ['jpg', 'png', 'pdf'],
      svg: ['png', 'jpg', 'pdf'],
      
      mp3: ['wav', 'ogg', 'flac'],
      wav: ['mp3', 'ogg', 'flac'],
      ogg: ['mp3', 'wav'],
      flac: ['mp3', 'wav', 'ogg'],
      aac: ['mp3', 'wav'],
      
      mp4: ['avi', 'webm', 'mov', 'mp3'],
      avi: ['mp4', 'webm', 'mov'],
      mov: ['mp4', 'webm', 'avi'],
      webm: ['mp4', 'avi'],
      mkv: ['mp4', 'avi', 'webm'],
    };

    return mapaFormatos[ext] || [];
  }, []);

  return {
    archivos,
    arrastrando,
    inputRef,
    alArrastrarSobre,
    alSalirDelArea,
    alSoltar,
    abrirSelector,
    alSeleccionar,
    actualizarArchivo,
    establecerFormatoSalida,
    actualizarProgreso,
    eliminarArchivo,
    limpiarArchivos,
    obtenerFormatosDisponibles,
  };
}
