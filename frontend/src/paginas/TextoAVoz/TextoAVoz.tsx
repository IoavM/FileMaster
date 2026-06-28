import { useState } from 'react';
import { Volume2, Download } from 'lucide-react';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import { textoAVoz, descargarBlob } from '../../servicios/api';
import '../Convertir/Convertir.css';

const VOCES = [
  { valor: 'es-MX-DaliaNeural', etiqueta: 'Dalia (México, femenina)' },
  { valor: 'es-MX-JorgeNeural', etiqueta: 'Jorge (México, masculina)' },
  { valor: 'es-ES-ElviraNeural', etiqueta: 'Elvira (España, femenina)' },
  { valor: 'es-ES-AlvaroNeural', etiqueta: 'Álvaro (España, masculina)' },
  { valor: 'es-AR-ElenaNeural', etiqueta: 'Elena (Argentina, femenina)' },
  { valor: 'es-CO-SalomeNeural', etiqueta: 'Salomé (Colombia, femenina)' },
];

export default function TextoAVoz() {
  const [texto, establecerTexto] = useState('');
  const [voz, establecerVoz] = useState('es-MX-DaliaNeural');
  const [velocidad, establecerVelocidad] = useState(1.0);
  const [generando, establecerGenerando] = useState(false);
  const [resultado, establecerResultado] = useState<string | null>(null);
  const [error, establecerError] = useState('');

  const generar = async () => {
    if (!texto.trim()) return;

    establecerGenerando(true);
    establecerError('');

    try {
      const blob = await textoAVoz(texto, voz, velocidad);
      const url = URL.createObjectURL(blob);
      establecerResultado(url);
    } catch {
      establecerError('Error al generar el audio. Verifica que el backend esté activo.');
    } finally {
      establecerGenerando(false);
    }
  };

  const descargar = () => {
    if (!resultado) return;
    fetch(resultado)
      .then((r) => r.blob())
      .then((blob) => descargarBlob(blob, 'texto-a-voz.mp3'));
  };

  return (
    <div className="pagina-herramienta">
      <div className="contenedor">
        <div className="pagina-herramienta-encabezado">
          <div className="pagina-herramienta-icono" style={{ background: '#EDE9FE', color: '#7C3AED' }}>
            <Volume2 />
          </div>
          <h1 className="pagina-herramienta-titulo">Texto a Voz</h1>
          <p className="pagina-herramienta-descripcion">
            Escribe o pega tu texto y conviértelo en audio con voces naturales.
          </p>
        </div>

        <div className="panel-herramienta">
          {}
          <div className="campo">
            <label className="campo-etiqueta" htmlFor="tts-texto">Texto a convertir</label>
            <textarea
              id="tts-texto"
              className="campo-input campo-textarea"
              placeholder="Escribe o pega el texto que deseas convertir a voz..."
              value={texto}
              onChange={(e) => establecerTexto(e.target.value)}
              maxLength={5000}
            />
            <p style={{ fontSize: 12, color: 'var(--color-secundario)', textAlign: 'right', marginTop: 4 }}>
              {texto.length}/5000 caracteres
            </p>
          </div>

          {}
          <div className="campo">
            <label className="campo-etiqueta" htmlFor="tts-voz">Voz</label>
            <select
              id="tts-voz"
              className="campo-input"
              value={voz}
              onChange={(e) => establecerVoz(e.target.value)}
            >
              {VOCES.map((v) => (
                <option key={v.valor} value={v.valor}>{v.etiqueta}</option>
              ))}
            </select>
          </div>

          {}
          <div className="campo">
            <label className="campo-etiqueta">Velocidad: {velocidad.toFixed(1)}x</label>
            <input
              type="range"
              className="campo-slider"
              min={0.5}
              max={2.0}
              step={0.1}
              value={velocidad}
              onChange={(e) => establecerVelocidad(Number(e.target.value))}
            />
          </div>

          {}
          <div className="acciones-herramienta">
            <BotonPrimario
              variante="primario"
              cargando={generando}
              onClick={generar}
              disabled={!texto.trim()}
              icono={<Volume2 size={18} />}
            >
              Generar Audio
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
              <audio controls src={resultado} className="resultado-audio" />
              <div className="acciones-herramienta">
                <BotonPrimario variante="primario" icono={<Download size={18} />} onClick={descargar}>
                  Descargar Audio
                </BotonPrimario>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
