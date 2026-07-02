import { useState } from 'react';
import { FileOutput, Download } from 'lucide-react';
import JSZip from 'jszip';
import AreaSubida from '../../componentes/AreaSubida/AreaSubida';
import SelectorFormato from '../../componentes/SelectorFormato/SelectorFormato';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import { usarSubidaArchivos } from '../../hooks/usarSubidaArchivos';
import { convertirArchivo, descargarBlob } from '../../servicios/api';
import './Convertir.css';

export default function Convertir() {
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
  } = usarSubidaArchivos();

  const [formatoSalida, establecerFormatoSalida] = useState('');
  const [progreso, establecerProgreso] = useState(0);
  const [convirtiendo, establecerConvirtiendo] = useState(false);
  const [resultados, establecerResultados] = useState<{ nombre: string; blob: Blob }[]>([]);
  const [estadoProcesamiento, establecerEstadoProcesamiento] = useState('');
  const [error, establecerError] = useState('');

  const archivoReferencia = archivos[0];
  const formatosDisponibles = archivoReferencia
    ? obtenerFormatosDisponibles(archivoReferencia.nombre)
    : [];

  const iniciarConversion = async () => {
    if (archivos.length === 0 || !formatoSalida) return;

    establecerConvirtiendo(true);
    establecerError('');
    establecerProgreso(0);
    establecerResultados([]);

    const nuevosResultados: { nombre: string; blob: Blob }[] = [];
    const totalArchivos = archivos.length;

    try {
      for (let i = 0; i < totalArchivos; i++) {
        const archivoActual = archivos[i];
        establecerEstadoProcesamiento(`Convirtiendo ${i + 1} de ${totalArchivos}: ${archivoActual.nombre}`);
        
        const alProgreso = (p: number) => {
          const progresoGlobal = Math.round(((i * 100) + p) / totalArchivos);
          establecerProgreso(progresoGlobal);
        };

        const blob = await convertirArchivo(
          archivoActual.archivo,
          formatoSalida,
          alProgreso
        );

        const nombreBase = archivoActual.nombre.replace(/\.[^/.]+$/, "");
        nuevosResultados.push({
          nombre: `${nombreBase}.${formatoSalida}`,
          blob
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

  return (
    <div className="pagina-herramienta">
      <div className="contenedor">
        <div className="pagina-herramienta-encabezado">
          <div className="pagina-herramienta-icono" style={{ background: '#DBEAFE', color: '#2563EB' }}>
            <FileOutput />
          </div>
          <h1 className="pagina-herramienta-titulo">Convertir Archivos</h1>
          <p className="pagina-herramienta-descripcion">
            Sube uno o varios archivos, selecciona el formato de salida y descarga el resultado.
          </p>
        </div>

        <div className="panel-herramienta">
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

          {archivoReferencia && formatosDisponibles.length > 0 && (
            <div className="campo" style={{ marginTop: 20 }}>
              <label className="campo-etiqueta">Formato de salida</label>
              <SelectorFormato
                formatos={formatosDisponibles}
                formatoSeleccionado={formatoSalida}
                alSeleccionar={establecerFormatoSalida}
                placeholder="Seleccionar formato"
              />
            </div>
          )}

          {convirtiendo && (
            <div style={{ marginTop: 20 }}>
              <BarraProgreso
                progreso={progreso}
                etiqueta={estadoProcesamiento}
                estado="convirtiendo"
              />
            </div>
          )}

          {error && (
            <div className="resultado-panel" style={{ background: '#FEE2E2', color: '#DC2626', marginTop: 20 }}>
              {error}
            </div>
          )}

          {resultados.length > 0 && (
            <div className="acciones-herramienta" style={{ marginTop: 20 }}>
              <BotonPrimario
                variante="primario"
                icono={<Download size={18} />}
                onClick={descargarResultado}
              >
                Descargar {resultados.length === 1 ? 'Archivo' : 'ZIP'}
              </BotonPrimario>
            </div>
          )}

          {archivoReferencia && formatoSalida && resultados.length === 0 && (
            <div className="acciones-herramienta" style={{ marginTop: 20 }}>
              <BotonPrimario
                variante="primario"
                cargando={convirtiendo}
                onClick={iniciarConversion}
                icono={<FileOutput size={18} />}
              >
                Convertir {archivos.length > 1 ? `(${archivos.length} archivos)` : ''}
              </BotonPrimario>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
