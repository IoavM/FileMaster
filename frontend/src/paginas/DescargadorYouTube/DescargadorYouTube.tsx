import { useState } from 'react';
import { Play, Download } from 'lucide-react';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import { descargarYouTube, descargarBlob } from '../../servicios/api';
import '../Convertir/Convertir.css';

export default function DescargadorYouTube() {
  const [url, establecerUrl] = useState('');
  const [formato, establecerFormato] = useState<'mp4' | 'mp3'>('mp4');
  const [descargando, establecerDescargando] = useState(false);
  const [progreso, establecerProgreso] = useState(0);
  const [error, establecerError] = useState('');

  const esUrlValida = (valor: string): boolean => {
    return /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/i.test(valor);
  };

  const descargar = async () => {
    if (!esUrlValida(url)) {
      establecerError('Ingresa una URL válida de YouTube.');
      return;
    }

    establecerDescargando(true);
    establecerError('');
    establecerProgreso(10);

    try {
      
      const intervalo = setInterval(() => {
        establecerProgreso((prev) => Math.min(prev + 5, 85));
      }, 1000);

      const blob = await descargarYouTube(url, formato);

      clearInterval(intervalo);
      establecerProgreso(100);

      const extension = formato === 'mp4' ? 'mp4' : 'mp3';
      descargarBlob(blob, `youtube-video.${extension}`);
    } catch {
      establecerError('Error al descargar. Verifica la URL y que el backend esté activo.');
    } finally {
      establecerDescargando(false);
      establecerProgreso(0);
    }
  };

  return (
    <div className="pagina-herramienta">
      <div className="contenedor">
        <div className="pagina-herramienta-encabezado">
          <div className="pagina-herramienta-icono" style={{ background: '#FEE2E2', color: '#DC2626' }}>
            <Play />
          </div>
          <h1 className="pagina-herramienta-titulo">Descargador de YouTube</h1>
          <p className="pagina-herramienta-descripcion">
            Pega el enlace de un video de YouTube y descárgalo en video o audio.
          </p>
        </div>

        <div className="panel-herramienta">
          {}
          <div className="campo">
            <label className="campo-etiqueta" htmlFor="yt-url">URL del Video</label>
            <input
              id="yt-url"
              className="campo-input"
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => establecerUrl(e.target.value)}
            />
          </div>

          {}
          <div className="campo">
            <label className="campo-etiqueta">Formato de descarga</label>
            <div className="grupo-botones">
              <BotonPrimario
                variante={formato === 'mp4' ? 'primario' : 'contorno'}
                onClick={() => establecerFormato('mp4')}
              >
                🎬 Video (MP4)
              </BotonPrimario>
              <BotonPrimario
                variante={formato === 'mp3' ? 'primario' : 'contorno'}
                onClick={() => establecerFormato('mp3')}
              >
                🎵 Audio (MP3)
              </BotonPrimario>
            </div>
          </div>

          {}
          {descargando && (
            <div style={{ marginTop: 20 }}>
              <BarraProgreso
                progreso={progreso}
                etiqueta="Descargando..."
                estado="convirtiendo"
              />
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
              variante="primario"
              cargando={descargando}
              onClick={descargar}
              disabled={!url.trim()}
              icono={<Download size={18} />}
            >
              Descargar
            </BotonPrimario>
          </div>
        </div>
      </div>
    </div>
  );
}
