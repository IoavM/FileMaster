import { useState, useRef, useEffect } from 'react';
import { FileText, Download, Upload, Merge, Scissors, Minimize2, RotateCw, GripVertical, ArrowUp, ArrowDown } from 'lucide-react';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import { editarPDF, descargarBlob } from '../../servicios/api';
import { formatearTamano } from '../../utilidades/formateadores';
import '../Convertir/Convertir.css';

type OperacionPDF = 'unir' | 'dividir' | 'comprimir' | 'rotar';

const OPERACIONES: { valor: OperacionPDF; etiqueta: string; icono: React.ElementType; descripcion: string }[] = [
  { valor: 'unir', etiqueta: 'Unir PDFs', icono: Merge, descripcion: 'Combinar varios PDFs en uno solo' },
  { valor: 'dividir', etiqueta: 'Dividir PDF', icono: Scissors, descripcion: 'Separar un PDF en páginas individuales o extraer un rango' },
  { valor: 'comprimir', etiqueta: 'Comprimir PDF', icono: Minimize2, descripcion: 'Reducir el tamaño del archivo PDF' },
  { valor: 'rotar', etiqueta: 'Rotar PDF', icono: RotateCw, descripcion: 'Rotar las páginas de un PDF' },
];

export default function EditorPDF() {
  const [operacion, establecerOperacion] = useState<OperacionPDF>('unir');
  const [archivos, establecerArchivos] = useState<File[]>([]);
  const [procesando, establecerProcesando] = useState(false);
  const [progreso, establecerProgreso] = useState(0);
  const [error, establecerError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const [desde, establecerDesde] = useState<number>(1);
  const [hasta, establecerHasta] = useState<number>(1);
  const [totalPaginas, establecerTotalPaginas] = useState<number | null>(null);

  const [arrastrandoIndice, establecerArrastrandoIndice] = useState<number | null>(null);

  const obtenerNumeroPaginasPDF = async (archivo: File): Promise<number> => {
    return new Promise((resolve) => {
      const lector = new FileReader();
      lector.onload = function (e) {
        const contenido = e.target?.result as string;
        const matches = contenido.match(/\/Count\s+(\d+)/);
        if (matches && matches[1]) {
          resolve(parseInt(matches[1], 10));
        } else {
          const matches2 = contenido.match(/\/Type\s*\/Pages\s*\/Count\s*(\d+)/);
          if (matches2 && matches2[1]) {
            resolve(parseInt(matches2[1], 10));
          } else {
            resolve(1);
          }
        }
      };
      lector.readAsText(archivo.slice(0, 1024 * 1024));
    });
  };

  useEffect(() => {
    if (operacion === 'dividir' && archivos.length > 0) {
      obtenerNumeroPaginasPDF(archivos[0]).then((paginas) => {
        establecerTotalPaginas(paginas);
        establecerDesde(1);
        establecerHasta(paginas);
      });
    } else {
      establecerTotalPaginas(null);
    }
  }, [operacion, archivos]);

  const alSeleccionar = (e: React.ChangeEvent<HTMLInputElement>) => {
    const lista = e.target.files;
    if (!lista) return;
    establecerArchivos((prev) => [...prev, ...Array.from(lista)]);
    establecerError('');
  };

  const eliminarArchivo = (indice: number) => {
    establecerArchivos((prev) => prev.filter((_, i) => i !== indice));
  };

  const alIniciarArrastre = (e: React.DragEvent, indice: number) => {
    establecerArrastrandoIndice(indice);
    e.dataTransfer.effectAllowed = 'move';
  };

  const alArrastrarSobreItem = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const alSoltarItem = (e: React.DragEvent, indiceDestino: number) => {
    e.preventDefault();
    if (arrastrandoIndice === null || arrastrandoIndice === indiceDestino) return;

    const nuevosArchivos = [...archivos];
    const [archivoMovido] = nuevosArchivos.splice(arrastrandoIndice, 1);
    nuevosArchivos.splice(indiceDestino, 0, archivoMovido);

    establecerArchivos(nuevosArchivos);
    establecerArrastrandoIndice(null);
  };

  const alFinalizarArrastre = () => {
    establecerArrastrandoIndice(null);
  };

  const moverArriba = (indice: number) => {
    if (indice === 0) return;
    const nuevosArchivos = [...archivos];
    const temp = nuevosArchivos[indice];
    nuevosArchivos[indice] = nuevosArchivos[indice - 1];
    nuevosArchivos[indice - 1] = temp;
    establecerArchivos(nuevosArchivos);
  };

  const moverAbajo = (indice: number) => {
    if (indice === archivos.length - 1) return;
    const nuevosArchivos = [...archivos];
    const temp = nuevosArchivos[indice];
    nuevosArchivos[indice] = nuevosArchivos[indice + 1];
    nuevosArchivos[indice + 1] = temp;
    establecerArchivos(nuevosArchivos);
  };

  const procesar = async () => {
    if (archivos.length === 0) return;

    establecerProcesando(true);
    establecerError('');
    establecerProgreso(0);

    try {
      const opciones = operacion === 'dividir' ? { desde, hasta } : {};
      const blob = await editarPDF(archivos, operacion, opciones, (p) => establecerProgreso(p));
      establecerProgreso(100);
      
      let nombreDescarga = `pdf-${operacion}.pdf`;
      if (operacion === 'dividir') {
        nombreDescarga = 'pdf-dividido.pdf';
      }
      
      descargarBlob(blob, nombreDescarga);
    } catch {
      establecerError('Error al procesar el PDF. Verifica que el backend esté activo.');
    } finally {
      establecerProcesando(false);
    }
  };

  const opActual = OPERACIONES.find((o) => o.valor === operacion)!;

  return (
    <div className="pagina-herramienta">
      <div className="contenedor">
        <div className="pagina-herramienta-encabezado">
          <div className="pagina-herramienta-icono" style={{ background: '#FEE2E2', color: '#DC2626' }}>
            <FileText />
          </div>
          <h1 className="pagina-herramienta-titulo">Editor PDF</h1>
          <p className="pagina-herramienta-descripcion">
            Unir, dividir, comprimir y rotar archivos PDF fácilmente.
          </p>
        </div>

        <div className="panel-herramienta">
          <div className="campo">
            <label className="campo-etiqueta">Operación</label>
            <div className="grupo-botones">
              {OPERACIONES.map((op) => (
                <BotonPrimario
                  key={op.valor}
                  variante={operacion === op.valor ? 'primario' : 'contorno'}
                  onClick={() => establecerOperacion(op.valor)}
                  icono={<op.icono size={16} />}
                >
                  {op.etiqueta}
                </BotonPrimario>
              ))}
            </div>
            <p style={{ marginTop: 8, fontSize: 13, color: 'var(--color-secundario)' }}>
              {opActual.descripcion}
            </p>
          </div>

          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            multiple={operacion === 'unir'}
            style={{ display: 'none' }}
            onChange={alSeleccionar}
          />

          <div
            className="area-subida"
            onClick={() => inputRef.current?.click()}
            style={{ cursor: 'pointer', padding: '24px 16px' }}
          >
            <div className="area-subida-icono">
              <Upload />
            </div>
            <h2 className="area-subida-titulo" style={{ fontSize: 16 }}>
              {operacion === 'unir' ? 'Sube los PDFs a unir' : 'Sube tu PDF'}
            </h2>
            <p className="area-subida-texto">Archivos PDF — máximo 50MB</p>
          </div>

          {archivos.length > 0 && (
            <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {archivos.map((archivo, indice) => (
                <div
                  key={indice}
                  className={`archivo-item ${arrastrandoIndice === indice ? 'arrastrando' : ''}`}
                  draggable={operacion === 'unir'}
                  onDragStart={(e) => alIniciarArrastre(e, indice)}
                  onDragOver={alArrastrarSobreItem}
                  onDragEnd={alFinalizarArrastre}
                  onDrop={(e) => alSoltarItem(e, indice)}
                  style={{
                    cursor: operacion === 'unir' ? 'grab' : 'default',
                    opacity: arrastrandoIndice === indice ? 0.5 : 1,
                    transition: 'all 0.2s ease',
                  }}
                >
                  {operacion === 'unir' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginRight: 8 }}>
                      <GripVertical size={16} style={{ color: 'var(--color-secundario)', cursor: 'grab' }} />
                      <span style={{ fontWeight: 'bold', minWidth: 20 }}>
                        {indice + 1}
                      </span>
                    </div>
                  )}

                  <FileText size={18} style={{ color: '#DC2626', flexShrink: 0 }} />

                  <div className="archivo-item-info">
                    <div className="archivo-item-nombre">{archivo.name}</div>
                    <div className="archivo-item-tamano">{formatearTamano(archivo.size)}</div>
                  </div>

                  {operacion === 'unir' && (
                    <div style={{ display: 'flex', gap: 4, marginRight: 8 }} onClick={(e) => e.stopPropagation()}>
                      <button
                        className="btn-orden"
                        onClick={() => moverArriba(indice)}
                        disabled={indice === 0}
                        style={{ padding: 4, opacity: indice === 0 ? 0.3 : 1, background: 'none', border: 'none', cursor: 'pointer' }}
                        title="Mover arriba"
                      >
                        <ArrowUp size={16} />
                      </button>
                      <button
                        className="btn-orden"
                        onClick={() => moverAbajo(indice)}
                        disabled={indice === archivos.length - 1}
                        style={{ padding: 4, opacity: indice === archivos.length - 1 ? 0.3 : 1, background: 'none', border: 'none', cursor: 'pointer' }}
                        title="Mover abajo"
                      >
                        <ArrowDown size={16} />
                      </button>
                    </div>
                  )}

                  <button className="archivo-item-eliminar" onClick={(e) => { e.stopPropagation(); eliminarArchivo(indice); }}>✕</button>
                </div>
              ))}
            </div>
          )}

          {operacion === 'dividir' && archivos.length > 0 && (
            <div className="rango-paginas" style={{ marginTop: 16, padding: 16, background: '#F8FAFC', borderRadius: 8 }}>
              <h3 style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 12, color: 'var(--color-texto)' }}>Rango de páginas a extraer</h3>
              <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: 12, color: 'var(--color-secundario)', display: 'block', marginBottom: 4 }}>Desde la página</label>
                  <input
                    type="number"
                    min={1}
                    max={hasta}
                    value={desde}
                    onChange={(e) => establecerDesde(Math.max(1, parseInt(e.target.value) || 1))}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid #CBD5E1', fontSize: 14 }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: 12, color: 'var(--color-secundario)', display: 'block', marginBottom: 4 }}>Hasta la página</label>
                  <input
                    type="number"
                    min={desde}
                    max={totalPaginas || undefined}
                    value={hasta}
                    onChange={(e) => establecerHasta(Math.max(desde, totalPaginas ? Math.min(totalPaginas, parseInt(e.target.value) || desde) : parseInt(e.target.value) || desde))}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid #CBD5E1', fontSize: 14 }}
                  />
                </div>
              </div>
              {totalPaginas && (
                <p style={{ marginTop: 8, fontSize: 12, color: 'var(--color-secundario)' }}>
                  El documento tiene un total de {totalPaginas} páginas.
                </p>
              )}
            </div>
          )}

          {procesando && (
            <div style={{ marginTop: 20 }}>
              <BarraProgreso progreso={progreso} etiqueta="Procesando..." estado="convirtiendo" />
            </div>
          )}

          {error && (
            <div className="resultado-panel" style={{ background: '#FEE2E2', color: '#DC2626', marginTop: 20 }}>
              {error}
            </div>
          )}

          <div className="acciones-herramienta" style={{ marginTop: 20 }}>
            <BotonPrimario
              variante="primario"
              cargando={procesando}
              onClick={procesar}
              disabled={archivos.length === 0}
              icono={<Download size={18} />}
            >
              {opActual.etiqueta} y Descargar
            </BotonPrimario>
          </div>
        </div>
      </div>
    </div>
  );
}
