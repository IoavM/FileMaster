import { useState, useEffect } from 'react';
import {
  Bot,
  Sparkles,
  User,
  Wand2,
  Copy,
  Check,
  Download,
  ArrowRight,
  RefreshCw,
  Sliders,
  AlertCircle,
  FileText,
  Activity,
  Zap,
} from 'lucide-react';
import {
  analizarTextoIA,
  humanizarTexto,
  analizarEstiloUsuario,
  type ResultadoAnalisisIA,
  type ResultadoHumanizacion,
  type PerfilEstiloUsuario,
} from '../../servicios/api';
import './DetectorHumanizador.css';

const EJEMPLO_IA =
  'En el vertiginoso mundo actual, la inteligencia artificial juega un papel crucial en la transformación digital de las empresas. ' +
  'Es importante destacar que las organizaciones deben adaptarse a estas nuevas dinámicas para mantenerse competitivas en el mercado. ' +
  'Asimismo, el aprendizaje automático ofrece un abanico de posibilidades sin precedentes en diversos sectores industriales. ' +
  'Por consiguiente, resulta fundamental establecer marcos éticos que garanticen un desarrollo responsable. ' +
  'En conclusión, nos encontramos ante un tapiz de innovaciones tecnológicas que forjarán el camino hacia el futuro.';

export default function DetectorHumanizador() {
  const [tabActivo, setTabActivo] = useState<'detector' | 'humanizador'>('detector');

  // Estado del Detector
  const [textoEntrada, setTextoEntrada] = useState('');
  const [analizando, setAnalizando] = useState(false);
  const [resultadoAnalisis, setResultadoAnalisis] = useState<ResultadoAnalisisIA | null>(null);
  const [errorDetector, setErrorDetector] = useState('');

  // Estado del Humanizador
  const [textoAHumanizar, setTextoAHumanizar] = useState('');
  const [modoHumanizador, setModoHumanizador] = useState<'automatico' | 'estilo_personal'>('automatico');
  const [nivelAuto, setNivelAuto] = useState<'casual' | 'equilibrado' | 'academico'>('equilibrado');
  const [textoMuestraUsuario, setTextoMuestraUsuario] = useState('');
  const [perfilUsuario, setPerfilUsuario] = useState<PerfilEstiloUsuario | null>(null);
  const [analizandoEstilo, setAnalizandoEstilo] = useState(false);
  const [humanizando, setHumanizando] = useState(false);
  const [resultadoHumanizado, setResultadoHumanizado] = useState<ResultadoHumanizacion | null>(null);
  const [errorHumanizador, setErrorHumanizador] = useState('');
  const [copiado, setCopiado] = useState(false);

  // Contador de palabras
  const palabrasEntrada = textoEntrada.trim() ? textoEntrada.trim().split(/\s+/).length : 0;
  const palabrasHumanizar = textoAHumanizar.trim() ? textoAHumanizar.trim().split(/\s+/).length : 0;

  // Analizar automáticamente el perfil de estilo del usuario cuando escribe una muestra
  useEffect(() => {
    if (!textoMuestraUsuario || textoMuestraUsuario.trim().length < 25) {
      setPerfilUsuario(null);
      return;
    }

    const timer = setTimeout(async () => {
      setAnalizandoEstilo(true);
      try {
        const perfil = await analizarEstiloUsuario(textoMuestraUsuario);
        setPerfilUsuario(perfil);
      } catch {
        setPerfilUsuario(null);
      } finally {
        setAnalizandoEstilo(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [textoMuestraUsuario]);

  // Ejecutar análisis de IA
  const ejecutarAnalisis = async (textoAProcesar?: string) => {
    const txt = textoAProcesar || textoEntrada;
    if (!txt.trim()) return;

    setAnalizando(true);
    setErrorDetector('');
    try {
      const res = await analizarTextoIA(txt);
      setResultadoAnalisis(res);
    } catch {
      setErrorDetector('Hubo un error al conectar con el motor de análisis. Verifica que el backend esté en ejecución.');
    } finally {
      setAnalizando(false);
    }
  };

  // Ejecutar humanización
  const ejecutarHumanizacion = async () => {
    if (!textoAHumanizar.trim()) return;

    setHumanizando(true);
    setErrorHumanizador('');
    try {
      const res = await humanizarTexto(
        textoAHumanizar,
        modoHumanizador,
        nivelAuto,
        modoHumanizador === 'estilo_personal' ? textoMuestraUsuario : undefined
      );
      setResultadoHumanizado(res);
    } catch {
      setErrorHumanizador('Error al humanizar el texto. Revisa la disponibilidad del servidor.');
    } finally {
      setHumanizando(false);
    }
  };

  // Copiar al portapapeles
  const copiarResultado = () => {
    if (!resultadoHumanizado?.texto_humanizado) return;
    navigator.clipboard.writeText(resultadoHumanizado.texto_humanizado);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
  };

  // Descargar texto humanizado
  const descargarTexto = () => {
    if (!resultadoHumanizado?.texto_humanizado) return;
    const blob = new Blob([resultadoHumanizado.texto_humanizado], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'texto-humanizado.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  // Pasar del detector al humanizador
  const pasarAHumanizar = () => {
    setTextoAHumanizar(textoEntrada);
    setTabActivo('humanizador');
    setResultadoHumanizado(null);
  };

  // Verificar texto humanizado en el detector
  const verificarEnDetector = () => {
    if (!resultadoHumanizado?.texto_humanizado) return;
    setTextoEntrada(resultadoHumanizado.texto_humanizado);
    setTabActivo('detector');
    ejecutarAnalisis(resultadoHumanizado.texto_humanizado);
  };

  return (
    <div className="pagina-herramienta">
      <div className="contenedor detector-ia-contenedor">
        {/* Encabezado principal */}
        <div className="pagina-herramienta-encabezado">
          <div className="pagina-herramienta-icono" style={{ background: '#EEF2FF', color: '#4F46E5' }}>
            <Bot size={28} />
          </div>
          <h1 className="pagina-herramienta-titulo">Detector y Humanizador IA</h1>
          <p className="pagina-herramienta-descripcion">
            Calcula el porcentaje exacto de IA en tus textos y humanízalos con ritmo natural o imitando tu propio estilo de redacción.
          </p>
        </div>

        {/* Pestañas de modo */}
        <div className="tabs-detector-ia">
          <button
            type="button"
            className={`tab-btn-ia ${tabActivo === 'detector' ? 'activo' : ''}`}
            onClick={() => setTabActivo('detector')}
          >
            <Activity size={18} />
            Detector de IA
          </button>
          <button
            type="button"
            className={`tab-btn-ia ${tabActivo === 'humanizador' ? 'activo' : ''}`}
            onClick={() => setTabActivo('humanizador')}
          >
            <Sparkles size={18} />
            Humanizador de Texto
          </button>
        </div>

        {/* =========================================================================
            PESTAÑA 1: DETECTOR DE IA
            ========================================================================= */}
        {tabActivo === 'detector' && (
          <div>
            <div className="tarjeta-editor-ia">
              <div className="tarjeta-editor-cabecera">
                <span className="tarjeta-editor-titulo">
                  <FileText size={18} />
                  Texto a analizar
                </span>
                <div className="tarjeta-editor-acciones-rapidas">
                  <button
                    type="button"
                    className="btn-accion-rapida"
                    onClick={() => {
                      setTextoEntrada(EJEMPLO_IA);
                      setResultadoAnalisis(null);
                    }}
                  >
                    Cargar ejemplo IA
                  </button>
                  {textoEntrada && (
                    <button
                      type="button"
                      className="btn-accion-rapida"
                      onClick={() => {
                        setTextoEntrada('');
                        setResultadoAnalisis(null);
                      }}
                    >
                      Limpiar
                    </button>
                  )}
                </div>
              </div>

              <textarea
                className="textarea-ia"
                placeholder="Pega aquí el texto que deseas analizar (ensayos, correos, artículos, párrafos generados por ChatGPT, Claude, etc.)..."
                value={textoEntrada}
                onChange={(e) => setTextoEntrada(e.target.value)}
              />

              <div className="editor-pie">
                <span>
                  {palabrasEntrada} palabras · {textoEntrada.length} caracteres
                </span>
                <div className="contenedor-boton-accion" style={{ margin: 0 }}>
                  <button
                    type="button"
                    className="btn-accion-ia"
                    onClick={() => ejecutarAnalisis()}
                    disabled={analizando || !textoEntrada.trim()}
                  >
                    {analizando ? (
                      <>
                        <RefreshCw size={18} className="animate-spin" />
                        Analizando texto...
                      </>
                    ) : (
                      <>
                        <Zap size={18} />
                        Analizar Probabilidad de IA
                      </>
                    )}
                  </button>
                </div>
              </div>

              {errorDetector && (
                <div style={{ marginTop: 14, color: '#DC2626', fontSize: 13, display: 'flex', gap: 6 }}>
                  <AlertCircle size={16} />
                  {errorDetector}
                </div>
              )}
            </div>

            {/* Resultados del Detector */}
            {resultadoAnalisis && (
              <div className="panel-resultado-detector">
                {/* Diagnóstico principal con Gauge */}
                <div className="tarjeta-diagnostico-principal">
                  <div className="circular-gauge">
                    <svg className="gauge-svg" viewBox="0 0 100 100">
                      <circle className="gauge-circulo-fondo" cx="50" cy="50" r="42" />
                      <circle
                        className="gauge-circulo-progreso"
                        cx="50"
                        cy="50"
                        r="42"
                        stroke={resultadoAnalisis.color}
                        strokeDasharray={2 * Math.PI * 42}
                        strokeDashoffset={2 * Math.PI * 42 * (1 - resultadoAnalisis.puntuacion_ia / 100)}
                      />
                    </svg>
                    <div className="gauge-texto-centro">
                      <div className="gauge-porcentaje" style={{ color: resultadoAnalisis.color }}>
                        {resultadoAnalisis.puntuacion_ia}%
                      </div>
                      <div className="gauge-subtexto">IA Estimada</div>
                    </div>
                  </div>

                  <div className="diagnostico-info">
                    <div className="diagnostico-titulo" style={{ color: resultadoAnalisis.color }}>
                      {resultadoAnalisis.etiqueta}
                    </div>
                    <div className="diagnostico-resumen">{resultadoAnalisis.resumen}</div>
                  </div>
                </div>

                {/* Métricas clave */}
                <div className="grid-metricas-ia">
                  <div className="card-metrica-item">
                    <div className="metrica-header">
                      <span>Ritmo / Burstiness</span>
                      <Activity size={14} />
                    </div>
                    <div className="metrica-valor">
                      {resultadoAnalisis.metricas.desviacion_ritmo > 6 ? 'Natural' : 'Monótono'}
                    </div>
                    <div className="metrica-desc">
                      Varianza de longitud: {resultadoAnalisis.metricas.desviacion_ritmo} pts (
                      {resultadoAnalisis.metricas.longitud_media_oraciones} palabras/oración promedio)
                    </div>
                  </div>

                  <div className="card-metrica-item">
                    <div className="metrica-header">
                      <span>Riqueza Léxica</span>
                      <Sparkles size={14} />
                    </div>
                    <div className="metrica-valor">{resultadoAnalisis.metricas.riqueza_lexica_pct}%</div>
                    <div className="metrica-desc">Diversidad de vocabulario sin repeticiones artificiales</div>
                  </div>

                  <div className="card-metrica-item">
                    <div className="metrica-header">
                      <span>Clichés de IA</span>
                      <AlertCircle size={14} />
                    </div>
                    <div className="metrica-valor">{resultadoAnalisis.metricas.cliches_detectados}</div>
                    <div className="metrica-desc">Muletillas y conectores sintéticos encontrados</div>
                  </div>
                </div>

                {/* Lista de clichés detectados */}
                {resultadoAnalisis.cliches.length > 0 && (
                  <div style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: '#64748B', marginBottom: 8 }}>
                      PATRONES IDENTIFICADOS:
                    </div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {resultadoAnalisis.cliches.map((c, i) => (
                        <span
                          key={i}
                          style={{
                            background: '#FEE2E2',
                            color: '#991B1B',
                            fontSize: 12,
                            fontWeight: 600,
                            padding: '3px 10px',
                            borderRadius: 6,
                          }}
                        >
                          "{c}"
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Visor Oración por Oración */}
                {resultadoAnalisis.oraciones.length > 0 && (
                  <div className="seccion-visor-oraciones">
                    <div className="visor-oraciones-titulo">
                      <span>Análisis Oración por Oración</span>
                      <div className="visor-leyenda">
                        <div className="leyenda-item">
                          <span className="punto-leyenda" style={{ background: '#10B981' }}></span> Humano
                        </div>
                        <div className="leyenda-item">
                          <span className="punto-leyenda" style={{ background: '#F59E0B' }}></span> Mixto
                        </div>
                        <div className="leyenda-item">
                          <span className="punto-leyenda" style={{ background: '#EF4444' }}></span> Probable IA
                        </div>
                      </div>
                    </div>

                    <div className="contenedor-texto-resaltado">
                      {resultadoAnalisis.oraciones.map((o) => (
                        <span
                          key={o.id}
                          className={`oracion-item ${o.nivel}`}
                          title={`Probabilidad IA: ${o.puntuacion_ia}% | ${o.palabras} palabras${o.cliches.length > 0 ? ` | Patrones: ${o.cliches.join(', ')}` : ''}`}
                        >
                          {o.texto}{' '}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Banner de llamada para humanizar */}
                <div className="banner-invitacion-humanizar">
                  <div>
                    <div className="banner-invitacion-texto">
                      ¿Quieres convertir este texto en 100% humano?
                    </div>
                    <div className="banner-invitacion-sub">
                      Elimina todos los patrones de IA y reescribe con cadencia natural o con tu propio estilo de redacción.
                    </div>
                  </div>
                  <button type="button" className="btn-banner-humanizar" onClick={pasarAHumanizar}>
                    <Wand2 size={16} />
                    Humanizar este texto
                    <ArrowRight size={16} />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            PESTAÑA 2: HUMANIZADOR DE TEXTO
            ========================================================================= */}
        {tabActivo === 'humanizador' && (
          <div>
            <div className="tarjeta-editor-ia">
              <div className="tarjeta-editor-cabecera">
                <span className="tarjeta-editor-titulo">
                  <Wand2 size={18} />
                  Texto a Humanizar
                </span>
                {textoAHumanizar && (
                  <button
                    type="button"
                    className="btn-accion-rapida"
                    onClick={() => {
                      setTextoAHumanizar('');
                      setResultadoHumanizado(null);
                    }}
                  >
                    Limpiar
                  </button>
                )}
              </div>

              <textarea
                className="textarea-ia"
                placeholder="Pega aquí el texto generado por IA que deseas humanizar..."
                value={textoAHumanizar}
                onChange={(e) => setTextoAHumanizar(e.target.value)}
              />

              <div className="editor-pie">
                <span>
                  {palabrasHumanizar} palabras · {textoAHumanizar.length} caracteres
                </span>
              </div>

              {/* Selector de Modos de Humanización */}
              <div className="seccion-selector-modo">
                <div className="selector-modo-titulo">
                  <Sliders size={16} />
                  Selecciona la Estrategia de Humanización:
                </div>

                <div className="grid-modos-humanizador">
                  {/* Modo Automático */}
                  <div
                    className={`card-modo-opcion ${modoHumanizador === 'automatico' ? 'activa' : ''}`}
                    onClick={() => setModoHumanizador('automatico')}
                  >
                    <div className="card-modo-header">
                      <Sparkles size={16} color="#2563EB" />
                      Humanización Automática
                    </div>
                    <div className="card-modo-desc">
                      Erradica muletillas robóticas y equilibra la longitud de oraciones para un flujo natural.
                    </div>
                  </div>

                  {/* Modo Estilo Personal del Usuario */}
                  <div
                    className={`card-modo-opcion ${modoHumanizador === 'estilo_personal' ? 'activa' : ''}`}
                    onClick={() => setModoHumanizador('estilo_personal')}
                  >
                    <div className="card-modo-header">
                      <User size={16} color="#16A34A" />
                      Mi Estilo Personal (Recomendado)
                    </div>
                    <div className="card-modo-desc">
                      Pega una muestra de tu autoría para clonar tus patrones de tono, longitud y vocabulario.
                    </div>
                  </div>
                </div>

                {/* Subopciones para Modo Automático */}
                {modoHumanizador === 'automatico' && (
                  <div className="selector-niveles-auto">
                    <span style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>Tono deseado:</span>
                    <button
                      type="button"
                      className={`btn-nivel-chip ${nivelAuto === 'casual' ? 'activo' : ''}`}
                      onClick={() => setNivelAuto('casual')}
                    >
                      Casual y Cercano
                    </button>
                    <button
                      type="button"
                      className={`btn-nivel-chip ${nivelAuto === 'equilibrado' ? 'activo' : ''}`}
                      onClick={() => setNivelAuto('equilibrado')}
                    >
                      Equilibrado (Estándar)
                    </button>
                    <button
                      type="button"
                      className={`btn-nivel-chip ${nivelAuto === 'academico' ? 'activo' : ''}`}
                      onClick={() => setNivelAuto('academico')}
                    >
                      Académico / Formal
                    </button>
                  </div>
                )}

                {/* Área de muestra personal del usuario */}
                {modoHumanizador === 'estilo_personal' && (
                  <div className="caja-estilo-personal">
                    <div className="caja-estilo-personal-titulo">
                      <User size={16} />
                      Muestra de tu redacción previa:
                    </div>
                    <div className="caja-estilo-personal-ayuda">
                      Pega aquí 1 o 2 párrafos que tú mismo hayas escrito (un correo, informe, ensayo o mensaje). El sistema extraerá tus patrones para aplicarlos al texto final.
                    </div>

                    <textarea
                      className="textarea-muestra-usuario"
                      placeholder="Ejemplo: Ayer estuve revisando los datos con mi equipo y la verdad me sorprendió el resultado. Creo que la clave está en simplificar el proceso..."
                      value={textoMuestraUsuario}
                      onChange={(e) => setTextoMuestraUsuario(e.target.value)}
                    />

                    {analizandoEstilo && (
                      <div style={{ fontSize: 12, color: '#16A34A', marginTop: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                        <RefreshCw size={12} className="animate-spin" /> Extrayendo tus patrones estilísticos...
                      </div>
                    )}

                    {perfilUsuario?.valido && (
                      <div className="badge-perfil-detectado">
                        <Check size={16} />
                        <span>
                          Tu Estilo Detectado: {perfilUsuario.resumen_estilo}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Botón de humanizar */}
              <div className="contenedor-boton-accion">
                <button
                  type="button"
                  className="btn-accion-ia"
                  onClick={ejecutarHumanizacion}
                  disabled={humanizando || !textoAHumanizar.trim()}
                >
                  {humanizando ? (
                    <>
                      <RefreshCw size={18} className="animate-spin" />
                      Humanizando texto...
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} />
                      Humanizar Texto Ahora
                    </>
                  )}
                </button>
              </div>

              {errorHumanizador && (
                <div style={{ marginTop: 14, color: '#DC2626', fontSize: 13, display: 'flex', gap: 6 }}>
                  <AlertCircle size={16} />
                  {errorHumanizador}
                </div>
              )}
            </div>

            {/* Resultado de Humanización */}
            {resultadoHumanizado && (
              <div className="panel-resultado-humanizado">
                {/* Banner de reducción */}
                <div className="banner-reduccion-ia">
                  <div className="reduccion-metricas-caja">
                    <span className="badge-antes">
                      Antes: {resultadoHumanizado.puntuacion_antes}% IA
                    </span>
                    <span className="badge-flecha">➔</span>
                    <span className="badge-despues">
                      Ahora: {resultadoHumanizado.puntuacion_despues}% IA
                    </span>
                  </div>

                  <div className="badge-reduccion-total">
                    <Check size={16} />
                    {resultadoHumanizado.reduccion_porcentual > 0
                      ? `-${resultadoHumanizado.reduccion_porcentual}% de IA eliminada`
                      : 'Texto optimizado para lectura humana'}
                  </div>
                </div>

                <div style={{ fontSize: 14, fontWeight: 700, color: '#0F172A', marginBottom: 8 }}>
                  Texto Humanizado:
                </div>

                <textarea
                  className="textarea-humanizado-salida"
                  readOnly
                  value={resultadoHumanizado.texto_humanizado}
                />

                <div className="acciones-salida-humanizada">
                  <button type="button" className="btn-accion-secundaria" onClick={copiarResultado}>
                    {copiado ? (
                      <>
                        <Check size={16} color="#16A34A" /> Copiado al portapapeles
                      </>
                    ) : (
                      <>
                        <Copy size={16} /> Copiar texto
                      </>
                    )}
                  </button>

                  <button type="button" className="btn-accion-secundaria" onClick={descargarTexto}>
                    <Download size={16} /> Descargar (.txt)
                  </button>

                  <button
                    type="button"
                    className="btn-accion-secundaria"
                    style={{ background: '#EEF2FF', color: '#4F46E5', borderColor: '#C7D2FE' }}
                    onClick={verificarEnDetector}
                  >
                    <Activity size={16} /> Verificar en Detector
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
