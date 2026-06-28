import { useState } from 'react';
import { FileOutput, Download } from 'lucide-react';
import AreaSubida from '../../componentes/AreaSubida/AreaSubida';
import SelectorFormato from '../../componentes/SelectorFormato/SelectorFormato';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import { usarSubidaArchivos } from '../../hooks/usarSubidaArchivos';
import { convertirArchivo, descargarBlob } from '../../servicios/api';
import { obtenerExtension } from '../../utilidades/formateadores';
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
  const [resultado, establecerResultado] = useState<Blob | null>(null);
  const [error, establecerError] = useState('');

  const archivoActual = archivos[0];
  const formatosDisponibles = archivoActual
    ? obtenerFormatosDisponibles(archivoActual.nombre)
    : [];

  const iniciarConversion = async () => {
    if (!archivoActual || !formatoSalida) return;

    establecerConvirtiendo(true);
    establecerError('');
    establecerProgreso(0);

    try {
      const blob = await convertirArchivo(
        archivoActual.archivo,
        formatoSalida,
        (p) => establecerProgreso(p),
      );
      establecerResultado(blob);
      establecerProgreso(100);
    } catch (err) {
      establecerError('Error al convertir el archivo. Verifica que el backend esté activo.');
      console.error('Error de conversión:', err);
    } finally {
      establecerConvirtiendo(false);
    }
  };

  const descargarResultado = () => {
    if (!resultado || !archivoActual) return;
    const nombreBase = archivoActual.nombre.replace(
      `.${obtenerExtension(archivoActual.nombre)}`,
      '',
    );
    descargarBlob(resultado, `${nombreBase}.${formatoSalida}`);
  };

  return (
    <div className="pagina-herramienta">
      <div className="contenedor">
        {}
        <div className="pagina-herramienta-encabezado">
          <div className="pagina-herramienta-icono" style={{ background: '#DBEAFE', color: '#2563EB' }}>
            <FileOutput />
          </div>
          <h1 className="pagina-herramienta-titulo">Convertir Archivos</h1>
          <p className="pagina-herramienta-descripcion">
            Sube tu archivo, selecciona el formato de salida y descarga el resultado.
          </p>
        </div>

        {}
        <div className="panel-herramienta">
          {}
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

          {}
          {archivoActual && formatosDisponibles.length > 0 && (
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

          {}
          {convirtiendo && (
            <div style={{ marginTop: 20 }}>
              <BarraProgreso
                progreso={progreso}
                etiqueta="Convirtiendo..."
                estado="convirtiendo"
              />
            </div>
          )}

          {}
          {error && (
            <div className="resultado-panel" style={{ background: '#FEE2E2', color: '#DC2626', marginTop: 20 }}>
              {error}
            </div>
          )}

          {}
          {resultado && (
            <div className="acciones-herramienta">
              <BotonPrimario
                variante="primario"
                icono={<Download size={18} />}
                onClick={descargarResultado}
              >
                Descargar Archivo
              </BotonPrimario>
            </div>
          )}

          {}
          {archivoActual && formatoSalida && !resultado && (
            <div className="acciones-herramienta">
              <BotonPrimario
                variante="primario"
                cargando={convirtiendo}
                onClick={iniciarConversion}
                icono={<FileOutput size={18} />}
              >
                Convertir
              </BotonPrimario>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
