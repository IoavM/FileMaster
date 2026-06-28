import { useState, useRef } from 'react';
import { ImageDown, Download, Upload } from 'lucide-react';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import { comprimirImagen, descargarBlob } from '../../servicios/api';
import { formatearTamano } from '../../utilidades/formateadores';
import '../Convertir/Convertir.css';

export default function CompresorImagenes() {
  const [archivo, establecerArchivo] = useState<File | null>(null);
  const [imagenPreview, establecerImagenPreview] = useState<string | null>(null);
  const [calidad, establecerCalidad] = useState(80);
  const [comprimiendo, establecerComprimiendo] = useState(false);
  const [progreso, establecerProgreso] = useState(0);
  const [resultado, establecerResultado] = useState<{ blob: Blob; url: string } | null>(null);
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
    establecerImagenPreview(URL.createObjectURL(archivoSel));
    establecerResultado(null);
    establecerError('');
  };

  const comprimir = async () => {
    if (!archivo) return;

    establecerComprimiendo(true);
    establecerError('');
    establecerProgreso(0);

    try {
      const blob = await comprimirImagen(archivo, calidad, (p) => establecerProgreso(p));
      const url = URL.createObjectURL(blob);
      establecerResultado({ blob, url });
      establecerProgreso(100);
    } catch {
      establecerError('Error al comprimir. Verifica que el backend esté activo.');
    } finally {
      establecerComprimiendo(false);
    }
  };

  const descargar = () => {
    if (!resultado) return;
    descargarBlob(resultado.blob, `imagen-comprimida.${archivo?.name.split('.').pop() || 'jpg'}`);
  };

  const porcentajeReduccion = archivo && resultado
    ? Math.round((1 - resultado.blob.size / archivo.size) * 100)
    : 0;

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
            style={{ display: 'none' }}
            onChange={alSeleccionar}
          />

          {!imagenPreview ? (
            <div className="area-subida" onClick={() => inputRef.current?.click()} style={{ cursor: 'pointer' }}>
              <div className="area-subida-icono">
                <Upload />
              </div>
              <h2 className="area-subida-titulo">Sube tu imagen</h2>
              <p className="area-subida-texto">JPG, PNG, WEBP — máximo 50MB</p>
            </div>
          ) : (
            <>
              {}
              <div className="resultado-panel">
                <img src={resultado?.url || imagenPreview} alt="Vista previa" className="resultado-imagen" />
                {archivo && (
                  <p style={{ marginTop: 12, fontSize: 13, color: 'var(--color-secundario)' }}>
                    Original: {formatearTamano(archivo.size)}
                    {resultado && (
                      <> → Comprimido: {formatearTamano(resultado.blob.size)} ({porcentajeReduccion}% reducido)</>
                    )}
                  </p>
                )}
              </div>

              {}
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

              {}
              {comprimiendo && (
                <div style={{ marginTop: 20 }}>
                  <BarraProgreso progreso={progreso} etiqueta="Comprimiendo..." estado="convirtiendo" />
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
                    establecerArchivo(null);
                    establecerImagenPreview(null);
                    establecerResultado(null);
                  }}
                >
                  Cambiar Imagen
                </BotonPrimario>
                {!resultado ? (
                  <BotonPrimario
                    variante="primario"
                    cargando={comprimiendo}
                    onClick={comprimir}
                    icono={<ImageDown size={18} />}
                  >
                    Comprimir
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
