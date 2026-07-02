import { useState, useRef } from 'react';
import { ImageDown, Download, Upload } from 'lucide-react';
import JSZip from 'jszip';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import { comprimirImagen, descargarBlob } from '../../servicios/api';
import { formatearTamano } from '../../utilidades/formateadores';
import '../Convertir/Convertir.css';

export default function CompresorImagenes() {
  const [archivos, establecerArchivos] = useState<File[]>([]);
  const [calidad, establecerCalidad] = useState(80);
  const [comprimiendo, establecerComprimiendo] = useState(false);
  const [progreso, establecerProgreso] = useState(0);
  const [resultados, establecerResultados] = useState<{ nombre: string; blob: Blob }[]>([]);
  const [estadoProcesamiento, establecerEstadoProcesamiento] = useState('');
  const [error, establecerError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const alSeleccionar = (e: React.ChangeEvent<HTMLInputElement>) => {
    const lista = e.target.files;
    if (!lista) return;

    const nuevasImagenes: File[] = [];
    let errorFicheros = '';

    Array.from(lista).forEach((archivo) => {
      if (!archivo.type.startsWith('image/')) {
        errorFicheros = 'Alguno de los archivos no es una imagen válida.';
      } else {
        nuevasImagenes.push(archivo);
      }
    });

    if (errorFicheros) {
      establecerError(errorFicheros);
    }
    
    if (nuevasImagenes.length > 0) {
      establecerArchivos((prev) => [...prev, ...nuevasImagenes]);
      establecerResultados([]);
      establecerError('');
    }
    
    if (inputRef.current) inputRef.current.value = '';
  };

  const comprimir = async () => {
    if (archivos.length === 0) return;

    establecerComprimiendo(true);
    establecerError('');
    establecerProgreso(0);
    establecerResultados([]);

    const nuevosResultados: { nombre: string; blob: Blob }[] = [];
    const totalArchivos = archivos.length;

    try {
      for (let i = 0; i < totalArchivos; i++) {
        const archivoActual = archivos[i];
        establecerEstadoProcesamiento(`Comprimiendo ${i + 1} de ${totalArchivos}: ${archivoActual.name}`);
        
        const alProgreso = (p: number) => {
          const progresoGlobal = Math.round(((i * 100) + p) / totalArchivos);
          establecerProgreso(progresoGlobal);
        };

        const blob = await comprimirImagen(archivoActual, calidad, alProgreso);
        nuevosResultados.push({
          nombre: archivoActual.name,
          blob
        });
      }

      establecerResultados(nuevosResultados);
      establecerProgreso(100);
      establecerEstadoProcesamiento('¡Compresión completada con éxito!');
    } catch {
      establecerError('Error al comprimir. Verifica que el backend esté activo.');
    } finally {
      establecerComprimiendo(false);
    }
  };

  const descargar = async () => {
    if (resultados.length === 0) return;

    if (resultados.length === 1) {
      descargarBlob(resultados[0].blob, `comprimido-${resultados[0].nombre}`);
    } else {
      establecerEstadoProcesamiento('Generando archivo ZIP...');
      const zip = new JSZip();
      resultados.forEach((r) => {
        zip.file(r.nombre, r.blob);
      });
      const content = await zip.generateAsync({ type: 'blob' });
      descargarBlob(content, 'imagenes-comprimidas.zip');
      establecerEstadoProcesamiento('¡ZIP descargado!');
    }
  };

  return (
    <div className="pagina-herramienta">
      <div className="contenedor">
        <div className="pagina-herramienta-encabezado">
          <div className="pagina-herramienta-icono" style={{ background: '#FEF3C7', color: '#F59E0B' }}>
            <ImageDown />
          </div>
          <h1 className="pagina-herramienta-titulo">Comprimir Imágenes</h1>
          <p className="pagina-herramienta-descripcion">
            Reduce el tamaño de tus imágenes ajustando la calidad de compresión.
          </p>
        </div>

        <div className="panel-herramienta">
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            multiple
            style={{ display: 'none' }}
            onChange={alSeleccionar}
          />

          <div className="area-subida" onClick={() => inputRef.current?.click()} style={{ cursor: 'pointer' }}>
            <div className="area-subida-icono">
              <Upload />
            </div>
            <h2 className="area-subida-titulo">Sube tus imágenes</h2>
            <p className="area-subida-texto">JPG, PNG, WEBP — máximo 50MB</p>
          </div>

          {archivos.length > 0 && (
            <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {archivos.map((archivo, indice) => {
                const res = resultados.find(r => r.nombre === archivo.name);
                const porcentaje = res 
                  ? Math.round((1 - res.blob.size / archivo.size) * 100)
                  : null;
                  
                return (
                  <div key={indice} className="archivo-item">
                    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minWidth: 0 }}>
                      <div className="archivo-item-nombre" style={{ fontWeight: 500 }}>{archivo.name}</div>
                      <div className="archivo-item-tamano">
                        Original: {formatearTamano(archivo.size)}
                        {res && (
                          <span style={{ color: '#16A34A', marginLeft: 8, fontWeight: 500 }}>
                            → Comprimido: {formatearTamano(res.blob.size)} ({porcentaje}% reducido)
                          </span>
                        )}
                      </div>
                    </div>
                    {resultados.length === 0 && !comprimiendo && (
                      <button 
                        className="archivo-item-eliminar" 
                        onClick={() => establecerArchivos(prev => prev.filter((_, i) => i !== indice))}
                      >
                        ✕
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {archivos.length > 0 && (
            <>
              <div className="campo" style={{ marginTop: 20 }}>
                <label className="campo-etiqueta">Calidad: {calidad}%</label>
                <input
                  type="range"
                  className="campo-slider"
                  min={10}
                  max={100}
                  step={5}
                  value={calidad}
                  onChange={(e) => establecerCalidad(Number(e.target.value))}
                />
              </div>

              {comprimiendo && (
                <div style={{ marginTop: 20 }}>
                  <BarraProgreso progreso={progreso} etiqueta={estadoProcesamiento} estado="convirtiendo" />
                </div>
              )}

              {error && (
                <div className="resultado-panel" style={{ background: '#FEE2E2', color: '#DC2626', marginTop: 20 }}>
                  {error}
                </div>
              )}

              <div className="acciones-herramienta" style={{ marginTop: 20 }}>
                <BotonPrimario
                  variante="secundario"
                  onClick={() => {
                    establecerArchivos([]);
                    establecerResultados([]);
                  }}
                >
                  Limpiar lista
                </BotonPrimario>
                {resultados.length === 0 ? (
                  <BotonPrimario
                    variante="primario"
                    cargando={comprimiendo}
                    onClick={comprimir}
                    icono={<ImageDown size={18} />}
                  >
                    Comprimir {archivos.length > 1 ? `(${archivos.length} imágenes)` : ''}
                  </BotonPrimario>
                ) : (
                  <BotonPrimario variante="primario" icono={<Download size={18} />} onClick={descargar}>
                    Descargar {resultados.length === 1 ? 'Imagen' : 'ZIP'}
                  </BotonPrimario>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
