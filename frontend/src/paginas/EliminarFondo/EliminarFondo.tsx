import { useState, useRef, useEffect } from 'react';
import { Eraser, Download, Upload } from 'lucide-react';
import JSZip from 'jszip';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import { eliminarFondo, descargarBlob } from '../../servicios/api';
import { formatearTamano } from '../../utilidades/formateadores';
import '../Convertir/Convertir.css';

export default function EliminarFondo() {
  const [archivos, establecerArchivos] = useState<File[]>([]);
  const [procesando, establecerProcesando] = useState(false);
  const [progreso, establecerProgreso] = useState(0);
  const [resultados, establecerResultados] = useState<{ nombre: string; blob: Blob }[]>([]);
  const [estadoProcesamiento, establecerEstadoProcesamiento] = useState('');
  const [error, establecerError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const [indicePreview, establecerIndicePreview] = useState<number>(0);
  const [urlsOriginales, establecerUrlsOriginales] = useState<Record<string, string>>({});
  const [urlsResultados, establecerUrlsResultados] = useState<Record<string, string>>({});

  useEffect(() => {
    return () => {
      Object.values(urlsOriginales).forEach((url) => URL.revokeObjectURL(url));
      Object.values(urlsResultados).forEach((url) => URL.revokeObjectURL(url));
    };
  }, [urlsOriginales, urlsResultados]);

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
      const nuevasUrls: Record<string, string> = {};
      nuevasImagenes.forEach((file) => {
        nuevasUrls[file.name] = URL.createObjectURL(file);
      });
      establecerUrlsOriginales((prev) => ({ ...prev, ...nuevasUrls }));

      establecerArchivos((prev) => [...prev, ...nuevasImagenes]);
      establecerResultados([]);
      establecerError('');
      establecerIndicePreview(archivos.length);
    }
    
    if (inputRef.current) inputRef.current.value = '';
  };

  const procesar = async () => {
    if (archivos.length === 0) return;

    establecerProcesando(true);
    establecerError('');
    establecerProgreso(0);
    establecerResultados([]);

    const nuevosResultados: { nombre: string; blob: Blob }[] = [];
    const totalArchivos = archivos.length;
    const nuevasUrlsResultados: Record<string, string> = {};

    try {
      for (let i = 0; i < totalArchivos; i++) {
        const archivoActual = archivos[i];
        establecerEstadoProcesamiento(`Eliminando fondo ${i + 1} de ${totalArchivos}: ${archivoActual.name}`);
        
        const alProgreso = (p: number) => {
          const progresoGlobal = Math.round(((i * 100) + p) / totalArchivos);
          establecerProgreso(progresoGlobal);
        };

        const blob = await eliminarFondo(archivoActual, alProgreso);
        const resNombre = archivoActual.name.replace(/\.[^/.]+$/, "") + ".png";
        nuevosResultados.push({
          nombre: resNombre,
          blob
        });

        nuevasUrlsResultados[archivoActual.name] = URL.createObjectURL(blob);
      }

      establecerUrlsResultados(nuevasUrlsResultados);
      establecerResultados(nuevosResultados);
      establecerProgreso(100);
      establecerEstadoProcesamiento('¡Eliminación de fondo completada!');
    } catch {
      establecerError('Error al eliminar el fondo. Verifica que el backend esté activo.');
    } finally {
      establecerProcesando(false);
    }
  };

  const descargar = async () => {
    if (resultados.length === 0) return;

    if (resultados.length === 1) {
      descargarBlob(resultados[0].blob, resultados[0].nombre);
    } else {
      establecerEstadoProcesamiento('Generando archivo ZIP...');
      const zip = new JSZip();
      resultados.forEach((r) => {
        zip.file(r.nombre, r.blob);
      });
      const content = await zip.generateAsync({ type: 'blob' });
      descargarBlob(content, 'imagenes-sin-fondo.zip');
      establecerEstadoProcesamiento('¡ZIP descargado!');
    }
  };

  const limpiarLista = () => {
    Object.values(urlsOriginales).forEach((url) => URL.revokeObjectURL(url));
    Object.values(urlsResultados).forEach((url) => URL.revokeObjectURL(url));
    establecerUrlsOriginales({});
    establecerUrlsResultados({});
    establecerArchivos([]);
    establecerResultados([]);
    establecerIndicePreview(0);
  };

  return (
    <div className="pagina-herramienta">
      <div className="contenedor">
        <div className="pagina-herramienta-encabezado">
          <div className="pagina-herramienta-icono" style={{ background: '#DCFCE7', color: '#16A34A' }}>
            <Eraser />
          </div>
          <h1 className="pagina-herramienta-titulo">Eliminar Fondo</h1>
          <p className="pagina-herramienta-descripcion">
            Sube una o varias imágenes y elimina el fondo de forma automática e inteligente.
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

          <div
            className="area-subida"
            onClick={() => inputRef.current?.click()}
            style={{ cursor: 'pointer' }}
          >
            <div className="area-subida-icono">
              <Upload />
            </div>
            <h2 className="area-subida-titulo">Sube tus imágenes</h2>
            <p className="area-subida-texto">JPG, PNG, WEBP — máximo 50MB</p>
          </div>

          {archivos.length > 0 && (
            <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {archivos.map((archivo, indice) => {
                const resNombre = archivo.name.replace(/\.[^/.]+$/, "") + ".png";
                const res = resultados.find(r => r.nombre === resNombre);
                const activo = indice === indicePreview;
                
                return (
                  <div 
                    key={indice} 
                    className="archivo-item"
                    onClick={() => establecerIndicePreview(indice)}
                    style={{
                      cursor: 'pointer',
                      border: activo ? '2px solid var(--color-primario)' : '1px solid #E2E8F0',
                      background: activo ? '#F0F9FF' : '#FFFFFF',
                    }}
                  >
                    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minWidth: 0 }}>
                      <div className="archivo-item-nombre" style={{ fontWeight: 500 }}>{archivo.name}</div>
                      <div className="archivo-item-tamano">
                        Original: {formatearTamano(archivo.size)}
                        {res && (
                          <span style={{ color: '#16A34A', marginLeft: 8, fontWeight: 500 }}>
                            → Fondo eliminado (PNG)
                          </span>
                        )}
                      </div>
                    </div>
                    {resultados.length === 0 && !procesando && (
                      <button 
                        className="archivo-item-eliminar" 
                        onClick={(e) => {
                          e.stopPropagation();
                          establecerArchivos(prev => prev.filter((_, i) => i !== indice));
                          if (indicePreview >= archivos.length - 1) {
                            establecerIndicePreview(Math.max(0, archivos.length - 2));
                          }
                        }}
                      >
                        ✕
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {archivos[indicePreview] && (
            <div style={{ marginTop: 24 }}>
              <div className="preview-comparar">
                <div className="preview-panel">
                  <p className="preview-panel-titulo">Original</p>
                  <img src={urlsOriginales[archivos[indicePreview].name]} alt="Imagen original" />
                </div>
                <div 
                  className="preview-panel" 
                  style={{
                    background: urlsResultados[archivos[indicePreview].name]
                      ? 'repeating-conic-gradient(#E5E7EB 0% 25%, transparent 0% 50%) 0 0 / 20px 20px'
                      : undefined,
                  }}
                >
                  <p className="preview-panel-titulo">Sin Fondo</p>
                  {urlsResultados[archivos[indicePreview].name] ? (
                    <img src={urlsResultados[archivos[indicePreview].name]} alt="Imagen sin fondo" />
                  ) : (
                    <p style={{ color: 'var(--color-secundario)', padding: 40, textAlign: 'center' }}>
                      Haz clic en "Eliminar Fondo" para procesar
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {archivos.length > 0 && (
            <>
              {procesando && (
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
                  onClick={limpiarLista}
                >
                  Limpiar lista
                </BotonPrimario>
                {resultados.length === 0 ? (
                  <BotonPrimario
                    variante="primario"
                    cargando={procesando}
                    onClick={procesar}
                    icono={<Eraser size={18} />}
                  >
                    Eliminar Fondo {archivos.length > 1 ? `(${archivos.length} imágenes)` : ''}
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
