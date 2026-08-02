import { useState, useRef, useEffect } from 'react';
import {
  FileText,
  Download,
  Upload,
  Merge,
  Scissors,
  Minimize2,
  RotateCw,
  GripVertical,
  ArrowUp,
  ArrowDown,
  Lock,
  Unlock,
  ArrowUpDown,
  PenTool,
  Languages,
} from 'lucide-react';
import BotonPrimario from '../../componentes/BotonPrimario/BotonPrimario';
import BarraProgreso from '../../componentes/BarraProgreso/BarraProgreso';
import { editarPDF, descargarBlob } from '../../servicios/api';
import { formatearTamano } from '../../utilidades/formateadores';
import '../Convertir/Convertir.css';

type OperacionPDF =
  | 'unir'
  | 'dividir'
  | 'comprimir'
  | 'rotar'
  | 'proteger'
  | 'desbloquear'
  | 'ordenar'
  | 'firmar'
  | 'traducir';

const OPERACIONES: {
  valor: OperacionPDF;
  etiqueta: string;
  icono: React.ElementType;
  descripcion: string;
}[] = [
  { valor: 'unir', etiqueta: 'Unir PDFs', icono: Merge, descripcion: 'Combinar varios PDFs en uno solo' },
  { valor: 'dividir', etiqueta: 'Dividir PDF', icono: Scissors, descripcion: 'Separar un PDF en páginas individuales o extraer un rango' },
  { valor: 'comprimir', etiqueta: 'Comprimir PDF', icono: Minimize2, descripcion: 'Reducir el tamaño del archivo PDF' },
  { valor: 'rotar', etiqueta: 'Rotar PDF', icono: RotateCw, descripcion: 'Rotar las páginas de un PDF' },
  { valor: 'proteger', etiqueta: 'Proteger PDF', icono: Lock, descripcion: 'Añadir contraseña y cifrar tu documento PDF' },
  { valor: 'desbloquear', etiqueta: 'Desbloquear PDF', icono: Unlock, descripcion: 'Eliminar la contraseña de un PDF protegido' },
  { valor: 'ordenar', etiqueta: 'Ordenar Páginas', icono: ArrowUpDown, descripcion: 'Cambiar el orden de las páginas de tu PDF' },
  { valor: 'firmar', etiqueta: 'Firmar PDF', icono: PenTool, descripcion: 'Estampar firma digital o imagen en el PDF' },
  { valor: 'traducir', etiqueta: 'Traducir PDF', icono: Languages, descripcion: 'Traducir el contenido textual del PDF a otro idioma' },
];

const IDIOMAS = [
  { codigo: 'es', nombre: 'Español' },
  { codigo: 'en', nombre: 'Inglés' },
  { codigo: 'fr', nombre: 'Francés' },
  { codigo: 'de', nombre: 'Alemán' },
  { codigo: 'it', nombre: 'Italiano' },
  { codigo: 'pt', nombre: 'Portugués' },
];

export default function EditorPDF() {
  const [operacion, establecerOperacion] = useState<OperacionPDF>('unir');
  const [archivos, establecerArchivos] = useState<File[]>([]);
  const [procesando, establecerProcesando] = useState(false);
  const [progreso, establecerProgreso] = useState(0);
  const [error, establecerError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Opciones específicas
  const [desde, establecerDesde] = useState<number | string>(1);
  const [hasta, establecerHasta] = useState<number | string>(1);
  const [totalPaginas, establecerTotalPaginas] = useState<number | null>(null);

  const [clave, establecerClave] = useState('');
  const [textoFirma, establecerTextoFirma] = useState('');
  const [imagenFirmaB64, establecerImagenFirmaB64] = useState('');
  const [idiomaDestino, establecerIdiomaDestino] = useState('es');
  const [ordenPaginas, establecerOrdenPaginas] = useState<number[]>([]);

  const [arrastrandoIndice, establecerArrastrandoIndice] = useState<number | null>(null);
  const [esMovil, establecerEsMovil] = useState(false);

  useEffect(() => {
    establecerEsMovil(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent));
  }, []);

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
    if (archivos.length > 0) {
      obtenerNumeroPaginasPDF(archivos[0]).then((paginas) => {
        establecerTotalPaginas(paginas);
        if (operacion === 'dividir') {
          establecerDesde(1);
          establecerHasta(paginas);
        }
        if (operacion === 'ordenar') {
          establecerOrdenPaginas(Array.from({ length: paginas }, (_, i) => i));
        }
      });
    } else {
      establecerTotalPaginas(null);
      establecerOrdenPaginas([]);
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

  const alCargarImagenFirma = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      establecerImagenFirmaB64(reader.result as string);
    };
    reader.readAsDataURL(file);
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

    if (operacion === 'unir') {
      const nuevosArchivos = [...archivos];
      const [archivoMovido] = nuevosArchivos.splice(arrastrandoIndice, 1);
      nuevosArchivos.splice(indiceDestino, 0, archivoMovido);
      establecerArchivos(nuevosArchivos);
    } else if (operacion === 'ordenar') {
      const nuevoOrden = [...ordenPaginas];
      const [pagMovida] = nuevoOrden.splice(arrastrandoIndice, 1);
      nuevoOrden.splice(indiceDestino, 0, pagMovida);
      establecerOrdenPaginas(nuevoOrden);
    }
    establecerArrastrandoIndice(null);
  };

  const alFinalizarArrastre = () => {
    establecerArrastrandoIndice(null);
  };

  const moverPaginaArriba = (indice: number) => {
    if (indice === 0) return;
    const nuevoOrden = [...ordenPaginas];
    const temp = nuevoOrden[indice];
    nuevoOrden[indice] = nuevoOrden[indice - 1];
    nuevoOrden[indice - 1] = temp;
    establecerOrdenPaginas(nuevoOrden);
  };

  const moverPaginaAbajo = (indice: number) => {
    if (indice === ordenPaginas.length - 1) return;
    const nuevoOrden = [...ordenPaginas];
    const temp = nuevoOrden[indice];
    nuevoOrden[indice] = nuevoOrden[indice + 1];
    nuevoOrden[indice + 1] = temp;
    establecerOrdenPaginas(nuevoOrden);
  };

  const procesar = async () => {
    if (archivos.length === 0) return;

    establecerProcesando(true);
    establecerError('');
    establecerProgreso(0);

    try {
      let opciones: Record<string, unknown> = {};

      if (operacion === 'dividir') {
        const numDesde = desde ? Math.max(1, Number(desde)) : 1;
        const numHasta = hasta
          ? (totalPaginas ? Math.min(totalPaginas, Number(hasta)) : Number(hasta))
          : (totalPaginas || 1);
        opciones = { desde: Math.min(numDesde, numHasta), hasta: Math.max(numDesde, numHasta) };
      } else if (operacion === 'proteger' || operacion === 'desbloquear') {
        if (!clave) {
          establecerError('Por favor ingresa la contraseña.');
          establecerProcesando(false);
          return;
        }
        opciones = { clave };
      } else if (operacion === 'ordenar') {
        opciones = { orden: ordenPaginas };
      } else if (operacion === 'firmar') {
        opciones = { texto_firma: textoFirma, imagen_firma: imagenFirmaB64 };
      } else if (operacion === 'traducir') {
        opciones = { idioma: idiomaDestino };
      }

      const blob = await editarPDF(archivos, operacion, opciones, (p) => establecerProgreso(p));
      establecerProgreso(100);

      const nombreDescarga = `pdf-${operacion}.pdf`;
      descargarBlob(blob, nombreDescarga);
    } catch {
      establecerError('Error al procesar el PDF. Verifica la contraseña o la disponibilidad del servidor.');
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
          <h1 className="pagina-herramienta-titulo">Editor PDF Completo</h1>
          <p className="pagina-herramienta-descripcion">
            Unir, dividir, comprimir, rotar, proteger, desbloquear, reordenar páginas, firmar y traducir PDFs.
          </p>
        </div>

        <div className="panel-herramienta">
          <div className="campo">
            <label className="campo-etiqueta">Operación</label>
            <div className="grupo-botones" style={{ flexWrap: 'wrap', gap: 8 }}>
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

          {/* Lista de archivos */}
          {archivos.length > 0 && (
            <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {archivos.map((archivo, indice) => (
                <div
                  key={indice}
                  className={`archivo-item ${arrastrandoIndice === indice ? 'arrastrando' : ''}`}
                  draggable={operacion === 'unir' && !esMovil}
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
                  <FileText size={18} style={{ color: '#DC2626', flexShrink: 0 }} />

                  <div className="archivo-item-info">
                    <div className="archivo-item-nombre">{archivo.name}</div>
                    <div className="archivo-item-tamano">{formatearTamano(archivo.size)}</div>
                  </div>

                  <button
                    className="archivo-item-eliminar"
                    onClick={(e) => {
                      e.stopPropagation();
                      eliminarArchivo(indice);
                    }}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* OPCIÓN: Dividir */}
          {operacion === 'dividir' && archivos.length > 0 && (
            <div className="rango-paginas" style={{ marginTop: 16, padding: 16, background: '#F8FAFC', borderRadius: 8 }}>
              <h3 style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 12, color: 'var(--color-texto)' }}>Rango de páginas a extraer</h3>
              <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: 12, color: 'var(--color-secundario)', display: 'block', marginBottom: 4 }}>Desde la página</label>
                  <input
                    type="number"
                    min={1}
                    value={desde}
                    onChange={(e) => establecerDesde(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid #CBD5E1', fontSize: 14 }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: 12, color: 'var(--color-secundario)', display: 'block', marginBottom: 4 }}>Hasta la página</label>
                  <input
                    type="number"
                    min={1}
                    value={hasta}
                    onChange={(e) => establecerHasta(e.target.value)}
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

          {/* OPCIÓN: Proteger / Desbloquear */}
          {(operacion === 'proteger' || operacion === 'desbloquear') && archivos.length > 0 && (
            <div style={{ marginTop: 16, padding: 16, background: '#F8FAFC', borderRadius: 8 }}>
              <h3 style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 8 }}>
                {operacion === 'proteger' ? 'Establecer Contraseña' : 'Ingresar Contraseña Actual'}
              </h3>
              <input
                type="password"
                placeholder="Contraseña..."
                value={clave}
                onChange={(e) => establecerClave(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: 6, border: '1px solid #CBD5E1', fontSize: 14 }}
              />
            </div>
          )}

          {/* OPCIÓN: Ordenar Páginas */}
          {operacion === 'ordenar' && ordenPaginas.length > 0 && (
            <div style={{ marginTop: 16, padding: 16, background: '#F8FAFC', borderRadius: 8 }}>
              <h3 style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 12 }}>Reordenar Páginas</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {ordenPaginas.map((numPagina, index) => (
                  <div
                    key={index}
                    draggable={!esMovil}
                    onDragStart={(e) => alIniciarArrastre(e, index)}
                    onDragOver={alArrastrarSobreItem}
                    onDragEnd={alFinalizarArrastre}
                    onDrop={(e) => alSoltarItem(e, index)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      padding: '8px 12px',
                      background: 'white',
                      border: '1px solid #E2E8F0',
                      borderRadius: 6,
                      cursor: 'grab',
                    }}
                  >
                    <GripVertical size={16} style={{ color: 'var(--color-secundario)' }} />
                    <span style={{ fontWeight: '600', fontSize: 14, flex: 1 }}>
                      Página {numPagina + 1}
                    </span>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <button
                        type="button"
                        onClick={() => moverPaginaArriba(index)}
                        disabled={index === 0}
                        style={{ padding: 4, background: 'none', border: 'none', cursor: 'pointer', opacity: index === 0 ? 0.3 : 1 }}
                      >
                        <ArrowUp size={16} />
                      </button>
                      <button
                        type="button"
                        onClick={() => moverPaginaAbajo(index)}
                        disabled={index === ordenPaginas.length - 1}
                        style={{ padding: 4, background: 'none', border: 'none', cursor: 'pointer', opacity: index === ordenPaginas.length - 1 ? 0.3 : 1 }}
                      >
                        <ArrowDown size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* OPCIÓN: Firmar PDF */}
          {operacion === 'firmar' && archivos.length > 0 && (
            <div style={{ marginTop: 16, padding: 16, background: '#F8FAFC', borderRadius: 8, display: 'flex', flexDirection: 'column', gap: 12 }}>
              <h3 style={{ fontSize: 14, fontWeight: 'bold' }}>Detalles de la Firma</h3>
              <div>
                <label style={{ fontSize: 12, color: 'var(--color-secundario)', display: 'block', marginBottom: 4 }}>Texto de la firma</label>
                <input
                  type="text"
                  placeholder="Ej. Juan Pérez - 02/08/2026"
                  value={textoFirma}
                  onChange={(e) => establecerTextoFirma(e.target.value)}
                  style={{ width: '100%', padding: '10px 14px', borderRadius: 6, border: '1px solid #CBD5E1', fontSize: 14 }}
                />
              </div>
              <div>
                <label style={{ fontSize: 12, color: 'var(--color-secundario)', display: 'block', marginBottom: 4 }}>O subir imagen de firma / sello (opcional)</label>
                <input type="file" accept="image/*" onChange={alCargarImagenFirma} style={{ fontSize: 13 }} />
                {imagenFirmaB64 && (
                  <div style={{ marginTop: 8 }}>
                    <img src={imagenFirmaB64} alt="Firma previa" style={{ maxHeight: 60, borderRadius: 4, border: '1px dashed #CBD5E1' }} />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* OPCIÓN: Traducir PDF */}
          {operacion === 'traducir' && archivos.length > 0 && (
            <div style={{ marginTop: 16, padding: 16, background: '#F8FAFC', borderRadius: 8 }}>
              <h3 style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 8 }}>Idioma de Destino</h3>
              <select
                value={idiomaDestino}
                onChange={(e) => establecerIdiomaDestino(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: 6, border: '1px solid #CBD5E1', fontSize: 14, background: 'white' }}
              >
                {IDIOMAS.map((idm) => (
                  <option key={idm.codigo} value={idm.codigo}>
                    {idm.nombre}
                  </option>
                ))}
              </select>
            </div>
          )}

          {procesando && (
            <div style={{ marginTop: 20 }}>
              <BarraProgreso progreso={progreso} etiqueta="Procesando PDF..." estado="convirtiendo" />
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

