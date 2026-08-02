import { useState, useEffect } from 'react';
import { FileOutput, Download, FileText } from 'lucide-react';
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
  } = usarSubidaArchivos();

  const { conversiones, agregarConversion, limpiarHistorial } = usarHistorial();

  const [formatoSalida, establecerFormatoSalida] = useState('');
  const [progreso, establecerProgreso] = useState(0);
  const [convirtiendo, establecerConvirtiendo] = useState(false);
  const [resultado, establecerResultado] = useState<Blob | null>(null);
  const [error, establecerError] = useState('');

  const archivoActual = archivos[0];
  const formatosDisponibles = archivoActual
    ? obtenerFormatosDisponibles(archivoActual.nombre)
    : [];

  useEffect(() => {
    establecerFormatoSalida('');
    establecerProgreso(0);
    establecerResultado(null);
    establecerError('');
  }, [archivoActual]);

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
      
      const url = URL.createObjectURL(blob);
      establecerResultado(blob);
      establecerProgreso(100);

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
    descargarBlob(resultado, `${nombreBase} - (${formatoSalida}).${formatoSalida}`);
  };

  return (
    <div className="inicio">
      <div className="contenedor">
        {}
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

            {}
            {archivoActual && (
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

                {}
                {convirtiendo && (
                  <div style={{ marginTop: 20, marginBottom: 20 }}>
                    <BarraProgreso
                      progreso={progreso}
                      etiqueta="Convirtiendo..."
                      estado="convirtiendo"
                    />
                  </div>
                )}

                {}
                {error && (
                  <div className="resultado-panel" style={{ background: '#FEE2E2', color: '#DC2626', marginTop: 16, marginBottom: 16 }}>
                    {error}
                  </div>
                )}

                {}
                <div className="acciones-herramienta" style={{ marginTop: 16, justifyContent: 'flex-start' }}>
                  {archivoActual && formatoSalida && !resultado && (
                    <BotonPrimario
                      variante="primario"
                      cargando={convirtiendo}
                      onClick={iniciarConversion}
                      icono={<FileOutput size={18} />}
                    >
                      Convertir Archivo
                    </BotonPrimario>
                  )}

                  {resultado && (
                    <div style={{ display: 'flex', gap: 12 }}>
                      <BotonPrimario
                        variante="primario"
                        icono={<Download size={18} />}
                        onClick={descargarResultado}
                      >
                        Descargar Resultado
                      </BotonPrimario>
                      <BotonPrimario
                        variante="secundario"
                        onClick={limpiarArchivos}
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

        {}
        <TablaConversiones
          conversiones={conversiones}
          alLimpiar={limpiarHistorial}
        />
      </div>
    </div>
  );
}
