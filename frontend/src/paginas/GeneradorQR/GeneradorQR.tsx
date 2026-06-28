import { useState } from 'react';
import { QrCode, Download } from 'lucide-react';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import { generarQR, descargarBlob } from '../../servicios/api';
import '../Convertir/Convertir.css';

export default function GeneradorQR() {
  const [contenido, establecerContenido] = useState('');
  const [tamano, establecerTamano] = useState(300);
  const [color, establecerColor] = useState('#000000');
  const [fondo, establecerFondo] = useState('#FFFFFF');
  const [generando, establecerGenerando] = useState(false);
  const [resultado, establecerResultado] = useState<string | null>(null);
  const [error, establecerError] = useState('');

  const generar = async () => {
    if (!contenido.trim()) return;

    establecerGenerando(true);
    establecerError('');

    try {
      const blob = await generarQR(contenido, tamano, color, fondo);
      const url = URL.createObjectURL(blob);
      establecerResultado(url);
    } catch {
      establecerError('Error al generar el código QR. Verifica que el backend esté activo.');
    } finally {
      establecerGenerando(false);
    }
  };

  const descargar = () => {
    if (!resultado) return;
    fetch(resultado)
      .then((r) => r.blob())
      .then((blob) => descargarBlob(blob, 'codigo-qr.png'));
  };

  return (
    <div className="pagina-herramienta">
      <div className="contenedor">
        <div className="pagina-herramienta-encabezado">
          <div className="pagina-herramienta-icono" style={{ background: '#F1F5F9', color: '#0F172A' }}>
            <QrCode />
          </div>
          <h1 className="pagina-herramienta-titulo">Generador de Código QR</h1>
          <p className="pagina-herramienta-descripcion">
            Ingresa una URL o texto y genera tu código QR personalizado al instante.
          </p>
        </div>

        <div className="panel-herramienta">
          {}
          <div className="campo">
            <label className="campo-etiqueta" htmlFor="qr-contenido">URL o Texto</label>
            <input
              id="qr-contenido"
              className="campo-input"
              type="text"
              placeholder="https://ejemplo.com o cualquier texto..."
              value={contenido}
              onChange={(e) => establecerContenido(e.target.value)}
            />
          </div>

          {}
          <div className="campo">
            <label className="campo-etiqueta">Tamaño: {tamano}px</label>
            <input
              type="range"
              className="campo-slider"
              min={100}
              max={600}
              step={50}
              value={tamano}
              onChange={(e) => establecerTamano(Number(e.target.value))}
            />
          </div>

          {}
          <div style={{ display: 'flex', gap: 16 }}>
            <div className="campo" style={{ flex: 1 }}>
              <label className="campo-etiqueta" htmlFor="qr-color">Color</label>
              <input
                id="qr-color"
                type="color"
                value={color}
                onChange={(e) => establecerColor(e.target.value)}
                style={{ width: '100%', height: 40, cursor: 'pointer', border: 'none', borderRadius: 8 }}
              />
            </div>
            <div className="campo" style={{ flex: 1 }}>
              <label className="campo-etiqueta" htmlFor="qr-fondo">Fondo</label>
              <input
                id="qr-fondo"
                type="color"
                value={fondo}
                onChange={(e) => establecerFondo(e.target.value)}
                style={{ width: '100%', height: 40, cursor: 'pointer', border: 'none', borderRadius: 8 }}
              />
            </div>
          </div>

          {}
          <div className="acciones-herramienta">
            <BotonPrimario
              variante="primario"
              cargando={generando}
              onClick={generar}
              disabled={!contenido.trim()}
              icono={<QrCode size={18} />}
            >
              Generar QR
            </BotonPrimario>
          </div>

          {}
          {error && (
            <div className="resultado-panel" style={{ background: '#FEE2E2', color: '#DC2626' }}>
              {error}
            </div>
          )}

          {}
          {resultado && (
            <div className="resultado-panel">
              <img src={resultado} alt="Código QR generado" className="resultado-imagen" />
              <div className="acciones-herramienta">
                <BotonPrimario variante="primario" icono={<Download size={18} />} onClick={descargar}>
                  Descargar QR
                </BotonPrimario>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
