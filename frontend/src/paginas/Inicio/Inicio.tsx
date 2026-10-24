import { useState, useEffect, useRef } from 'react';
import { FileOutput, Download, FileText, RefreshCw } from 'lucide-react';
import JSZip from 'jszip';
import AreaSubida from '../../componentes/AreaSubida/AreaSubida';
import AtajosRapidos from '../../componentes/AtajosRapidos/AtajosRapidos';
import TablaConversiones from '../../componentes/TablaConversiones/TablaConversiones';
import SelectorFormato from '../../componentes/SelectorFormato/SelectorFormato';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import { usarSubidaArchivos } from '../../hooks/usarSubidaArchivos';
import { usarHistorial } from '../../hooks/usarHistorial';
import { convertirArchivo, descargarBlob } from '../../servicios/api';
import { obtenerExtension, formatearTamano } from '../../utilidades/formateadores';
import './Inicio.css';

export default function Inicio() {
  const {
    archivos,
    arrastrando,
    inputRef,
    alArrastrarSobre,
    alSalirDelArea,
    alSoltar,
    abrirSelector,
    alSeleccionar,
    eliminarArchivo,
    obtenerFormatosDisponibles,
    limpiarArchivos,
  } = usarSubidaArchivos({ reemplazarAlSubir: true });

  const { conversiones, agregarConversion, limpiarHistorial } = usarHistorial();

  const [formatoSalida, establecerFormatoSalida] = useState('');
  const [progreso, establecerProgreso] = useState(0);
  const [convirtiendo, establecerConvirtiendo] = useState(false);
  const [resultados, establecerResultados] = useState<{ id: string; nombre: string; blob: Blob }[]>([]);
  const [estadoProcesamiento, establecerEstadoProcesamiento] = useState('');
  const [error, establecerError] = useState('');

  const archivoReferencia = archivos[0];
  const formatosDisponibles = archivoReferencia
    ? obtenerFormatosDisponibles(archivoReferencia.nombre)
    : [];

  const refArchivosIds = useRef<string>('');

  // Sincronizar y limpiar estado cuando cambia la lista de archivos
  useEffect(() => {
    const idsActuales = archivos.map((a) => a.id).join(',');
    if (idsActuales !== refArchivosIds.current) {
      refArchivosIds.current = idsActuales;
      establecerProgreso(0);
      establecerResultados([]);
      establecerEstadoProcesamiento('');
      establecerError('');

      // Si el formato de salida previamente elegido ya no está en los disponibles, resetearlo
      if (formatoSalida) {
        const disponibles = archivoReferencia
          ? obtenerFormatosDisponibles(archivoReferencia.nombre)
          : [];
        if (!disponibles.includes(formatoSalida)) {
          establecerFormatoSalida('');
        }
      }
    }
  }, [archivos, archivoReferencia, formatoSalida, obtenerFormatosDisponibles]);

  const iniciarConversion = async () => {
    if (archivos.length === 0 || !formatoSalida) return;

    establecerConvirtiendo(true);
    establecerError('');
    establecerProgreso(0);
    establecerResultados([]);

    const nuevosResultados: { id: string; nombre: string; blob: Blob }[] = [];
    const totalArchivos = archivos.length;

    try {
      for (let i = 0; i < totalArchivos; i++) {
        const archivoActual = archivos[i];
        establecerEstadoProcesamiento(
          totalArchivos > 1
            ? `Convirtiendo ${i + 1} de ${totalArchivos}: ${archivoActual.nombre}`
            : `Convirtiendo ${archivoActual.nombre}...`
        );

        const alProgreso = (p: number) => {
          const progresoGlobal = Math.round(((i * 100) + p) / totalArchivos);
          establecerProgreso(progresoGlobal);
        };

        const blob = await convertirArchivo(
          archivoActual.archivo,
          formatoSalida,
          alProgreso,
        );

        const nombreBase = archivoActual.nombre.replace(/\.[^/.]+$/, '');
        const esZip = blob.type === 'application/zip';
        const ext = esZip ? 'zip' : formatoSalida;
        const nombreResultado = `${nombreBase}-convertido.${ext}`;

        nuevosResultados.push({
          id: archivoActual.id,
          nombre: nombreResultado,
          blob,
        });

        const url = URL.createObjectURL(blob);
        agregarConversion({
          id: archivoActual.id,
          nombreArchivo: archivoActual.nombre,
          formatoEntrada: obtenerExtension(archivoActual.nombre),
          formatoSalida: formatoSalida,
          tamano: formatearTamano(archivoActual.tamano),
          estado: 'completado',
          fecha: new Date().toISOString(),
          urlDescarga: url,
        });
      }

      establecerResultados(nuevosResultados);
      establecerProgreso(100);
      establecerEstadoProcesamiento('¡Conversión completada con éxito!');
    } catch (err) {
      establecerError('Error al convertir los archivos. Verifica que el backend esté activo.');
      console.error('Error de conversión:', err);
    } finally {
      establecerConvirtiendo(false);
    }
  };

  const descargarResultado = async () => {
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
      descargarBlob(content, 'archivos-convertidos.zip');
      establecerEstadoProcesamiento('¡ZIP descargado!');
    }
  };

  const reiniciarTodo = () => {
    limpiarArchivos();
    establecerFormatoSalida('');
    establecerResultados([]);
    establecerProgreso(0);
    establecerError('');
    establecerEstadoProcesamiento('');
  };

  return (
    <div className="inicio">
      <div className="contenedor">
        <div className="inicio-principal">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <AreaSubida
              archivos={archivos}
              arrastrando={arrastrando}
              inputRef={inputRef}
              alArrastrarSobre={alArrastrarSobre}
              alSalirDelArea={alSalirDelArea}
              alSoltar={alSoltar}
              abrirSelector={abrirSelector}
              alSeleccionar={alSeleccionar}
              eliminarArchivo={eliminarArchivo}
            />

            {archivoReferencia && (
              <div className="panel-herramienta" style={{ marginTop: 0 }}>
                <h3 className="campo-etiqueta" style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 15, marginBottom: 16 }}>
                  <FileText size={18} style={{ color: 'var(--color-primario)' }} />
                  Configurar Conversión
                </h3>

                {formatosDisponibles.length > 0 ? (
                  <div className="campo">
                    <label className="campo-etiqueta" htmlFor="select-formato">Convertir a:</label>
                    <SelectorFormato
                      formatos={formatosDisponibles}
                      formatoSeleccionado={formatoSalida}
                      alSeleccionar={establecerFormatoSalida}
                      placeholder="Seleccionar formato"
                    />
                  </div>
                ) : (
                  <p style={{ fontSize: 13, color: 'var(--color-error)' }}>
                    No hay formatos de conversión directa disponibles para este tipo de archivo. Prueba usando una de las herramientas del menú superior.
                  </p>
                )}

                {convirtiendo && (
                  <div style={{ marginTop: 20, marginBottom: 20 }}>
                    <BarraProgreso
                      progreso={progreso}
                      etiqueta={estadoProcesamiento || 'Convirtiendo...'}
                      estado="convirtiendo"
                    />
                  </div>
                )}

                {error && (
                  <div className="resultado-panel" style={{ background: '#FEE2E2', color: '#DC2626', marginTop: 16, marginBottom: 16 }}>
                    {error}
                  </div>
                )}

                <div className="acciones-herramienta" style={{ marginTop: 16, justifyContent: 'flex-start' }}>
                  {archivoReferencia && formatoSalida && resultados.length === 0 && (
                    <BotonPrimario
                      variante="primario"
                      cargando={convirtiendo}
                      onClick={iniciarConversion}
                      icono={<FileOutput size={18} />}
                    >
                      Convertir {archivos.length > 1 ? `(${archivos.length} archivos)` : 'Archivo'}
                    </BotonPrimario>
                  )}

                  {resultados.length > 0 && (
                    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                      <BotonPrimario
                        variante="primario"
                        icono={<Download size={18} />}
                        onClick={descargarResultado}
                      >
                        Descargar {resultados.length === 1 ? 'Resultado' : 'ZIP'}
                      </BotonPrimario>
                      <BotonPrimario
                        variante="secundario"
                        icono={<RefreshCw size={16} />}
                        onClick={reiniciarTodo}
                      >
                        Convertir otro archivo
                      </BotonPrimario>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <AtajosRapidos />
        </div>

        <TablaConversiones
          conversiones={conversiones}
          alLimpiar={limpiarHistorial}
        />
      </div>
    </div>
  );
}
