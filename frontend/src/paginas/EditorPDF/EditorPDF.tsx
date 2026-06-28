import { useState, useRef } from 'react';
import { FileText, Download, Upload, Merge, Scissors, Minimize2, RotateCw } from 'lucide-react';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import { editarPDF, descargarBlob } from '../../servicios/api';
import { formatearTamano } from '../../utilidades/formateadores';
import '../Convertir/Convertir.css';

type OperacionPDF = 'unir' | 'dividir' | 'comprimir' | 'rotar';

const OPERACIONES: { valor: OperacionPDF; etiqueta: string; icono: React.ElementType; descripcion: string }[] = [
  { valor: 'unir', etiqueta: 'Unir PDFs', icono: Merge, descripcion: 'Combinar varios PDFs en uno solo' },
  { valor: 'dividir', etiqueta: 'Dividir PDF', icono: Scissors, descripcion: 'Separar un PDF en páginas individuales' },
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

  const alSeleccionar = (e: React.ChangeEvent<HTMLInputElement>) => {
    const lista = e.target.files;
    if (!lista) return;
    establecerArchivos((prev) => [...prev, ...Array.from(lista)]);
    establecerError('');
  };

  const eliminarArchivo = (indice: number) => {
    establecerArchivos((prev) => prev.filter((_, i) => i !== indice));
  };

  const procesar = async () => {
    if (archivos.length === 0) return;

    establecerProcesando(true);
    establecerError('');
    establecerProgreso(0);

    try {
      const blob = await editarPDF(archivos, operacion, {}, (p) => establecerProgreso(p));
      establecerProgreso(100);
      descargarBlob(blob, `pdf-${operacion}.pdf`);
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
          {}
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

          {}
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

          {}
          {archivos.length > 0 && (
            <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {archivos.map((archivo, indice) => (
                <div key={indice} className="archivo-item">
                  <FileText size={18} style={{ color: '#DC2626', flexShrink: 0 }} />
                  <div className="archivo-item-info">
                    <div className="archivo-item-nombre">{archivo.name}</div>
                    <div className="archivo-item-tamano">{formatearTamano(archivo.size)}</div>
                  </div>
                  <button className="archivo-item-eliminar" onClick={() => eliminarArchivo(indice)}>✕</button>
                </div>
              ))}
            </div>
          )}

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
