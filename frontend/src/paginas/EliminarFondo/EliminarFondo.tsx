import { useState, useRef } from 'react';
import { Eraser, Download, Upload } from 'lucide-react';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import { eliminarFondo, descargarBlob } from '../../servicios/api';
import '../Convertir/Convertir.css';

export default function EliminarFondo() {
  const [imagenOriginal, establecerImagenOriginal] = useState<string | null>(null);
  const [archivo, establecerArchivo] = useState<File | null>(null);
  const [resultado, establecerResultado] = useState<string | null>(null);
  const [procesando, establecerProcesando] = useState(false);
  const [progreso, establecerProgreso] = useState(0);
  const [error, establecerError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const alSeleccionar = (e: React.ChangeEvent<HTMLInputElement>) => {
    const archivoSel = e.target.files?.[0];
    if (!archivoSel) return;

    if (!archivoSel.type.startsWith('image/')) {
      establecerError('Selecciona un archivo de imagen válido.');
      return;
    }

    establecerArchivo(archivoSel);
    establecerImagenOriginal(URL.createObjectURL(archivoSel));
    establecerResultado(null);
    establecerError('');
  };

  const procesar = async () => {
    if (!archivo) return;

    establecerProcesando(true);
    establecerError('');
    establecerProgreso(0);

    try {
      const blob = await eliminarFondo(archivo, (p) => establecerProgreso(p));
      const url = URL.createObjectURL(blob);
      establecerResultado(url);
      establecerProgreso(100);
    } catch {
      establecerError('Error al eliminar el fondo. Verifica que el backend esté activo.');
    } finally {
      establecerProcesando(false);
    }
  };

  const descargar = () => {
    if (!resultado) return;
    fetch(resultado)
      .then((r) => r.blob())
      .then((blob) => descargarBlob(blob, 'imagen-sin-fondo.png'));
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
            Sube una imagen y elimina el fondo de forma automática e inteligente.
          </p>
        </div>

        <div className="panel-herramienta">
          {}
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={alSeleccionar}
          />

          {!imagenOriginal ? (
            <div
              className="area-subida"
              onClick={() => inputRef.current?.click()}
              style={{ cursor: 'pointer' }}
            >
              <div className="area-subida-icono">
                <Upload />
              </div>
              <h2 className="area-subida-titulo">Sube tu imagen</h2>
              <p className="area-subida-texto">JPG, PNG, WEBP — máximo 50MB</p>
            </div>
          ) : (
            <>
              {}
              <div className="preview-comparar">
                <div className="preview-panel">
                  <p className="preview-panel-titulo">Original</p>
                  <img src={imagenOriginal} alt="Imagen original" />
                </div>
                <div className="preview-panel" style={{
                  background: resultado
                    ? 'repeating-conic-gradient(#E5E7EB 0% 25%, transparent 0% 50%) 0 0 / 20px 20px'
                    : undefined,
                }}>
                  <p className="preview-panel-titulo">Sin Fondo</p>
                  {resultado ? (
                    <img src={resultado} alt="Imagen sin fondo" />
                  ) : (
                    <p style={{ color: 'var(--color-secundario)', padding: 40 }}>
                      Haz clic en "Eliminar Fondo" para procesar
                    </p>
                  )}
                </div>
              </div>

              {}
              {procesando && (
                <div style={{ marginTop: 20 }}>
                  <BarraProgreso progreso={progreso} etiqueta="Procesando..." estado="convirtiendo" />
                </div>
              )}

              {}
              {error && (
                <div className="resultado-panel" style={{ background: '#FEE2E2', color: '#DC2626' }}>
                  {error}
                </div>
              )}

              {}
              <div className="acciones-herramienta">
                <BotonPrimario
                  variante="secundario"
                  onClick={() => {
                    establecerImagenOriginal(null);
                    establecerResultado(null);
                    establecerArchivo(null);
                  }}
                >
                  Cambiar Imagen
                </BotonPrimario>
                {!resultado ? (
                  <BotonPrimario
                    variante="primario"
                    cargando={procesando}
                    onClick={procesar}
                    icono={<Eraser size={18} />}
                  >
                    Eliminar Fondo
                  </BotonPrimario>
                ) : (
                  <BotonPrimario variante="primario" icono={<Download size={18} />} onClick={descargar}>
                    Descargar
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
