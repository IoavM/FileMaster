import { useRef } from 'react';
import {
  CloudUpload,
  FileText,
  FileSpreadsheet,
  FileImage,
  X,
} from 'lucide-react';
import type { ArchivoSubido } from '../../interfaces/tipos';
import { formatearTamano } from '../../utilidades/formateadores';
import './AreaSubida.css';

const FORMATOS_VISIBLES = [
  {
    etiqueta: 'PDF',
    clase: 'pdf',
    icono: FileText,
    accept: 'application/pdf,.pdf',
  },
  {
    etiqueta: 'XLSX',
    clase: 'xlsx',
    icono: FileSpreadsheet,
    accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,.xlsx,.xls',
  },
  {
    etiqueta: 'DOCX',
    clase: 'docx',
    icono: FileText,
    accept: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword,.docx,.doc',
  },
  {
    etiqueta: 'JPG/PNG',
    clase: 'img',
    icono: FileImage,
    accept: 'image/jpeg,image/png,image/webp,image/gif,image/bmp,.jpg,.jpeg,.png,.webp,.gif,.bmp',
  },
];

interface PropiedadesAreaSubida {
  archivos: ArchivoSubido[];
  arrastrando: boolean;
  inputRef: React.RefObject<HTMLInputElement | null>;
  alArrastrarSobre: (e: React.DragEvent) => void;
  alSalirDelArea: (e: React.DragEvent) => void;
  alSoltar: (e: React.DragEvent) => void;
  abrirSelector: () => void;
  alSeleccionar: (e: React.ChangeEvent<HTMLInputElement>) => void;
  eliminarArchivo: (id: string) => void;
}

function BotonFormato({
  formato,
  alSeleccionar,
}: {
  formato: (typeof FORMATOS_VISIBLES)[0];
  alSeleccionar: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  const localInputRef = useRef<HTMLInputElement | null>(null);

  const alHacerClic = (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (localInputRef.current) {
      localInputRef.current.value = '';
      localInputRef.current.click();
    }
  };

  return (
    <>
      <input
        ref={localInputRef}
        type="file"
        multiple
        accept={formato.accept}
        className="area-subida-input"
        onChange={alSeleccionar}
      />
      <button
        className="formato-badge"
        type="button"
        onClick={alHacerClic}
        title={`Seleccionar solo archivos ${formato.etiqueta}`}
      >
        <formato.icono className={`formato-badge-icono ${formato.clase}`} />
        {formato.etiqueta}
      </button>
    </>
  );
}

export default function AreaSubida({
  archivos,
  arrastrando,
  inputRef,
  alArrastrarSobre,
  alSalirDelArea,
  alSoltar,
  abrirSelector,
  alSeleccionar,
  eliminarArchivo,
}: PropiedadesAreaSubida) {
  return (
    <div
      className={`area-subida ${arrastrando ? 'arrastrando' : ''}`}
      onDragOver={alArrastrarSobre}
      onDragLeave={alSalirDelArea}
      onDrop={alSoltar}
      onClick={abrirSelector}
      id="area-subida"
    >
      {/* Input general */}
      <input
        ref={inputRef}
        type="file"
        multiple
        className="area-subida-input"
        onChange={alSeleccionar}
        accept=".pdf,.doc,.docx,.xls,.xlsx,.pptx,.txt,.csv,.jpg,.jpeg,.png,.gif,.webp,.svg,.bmp,.tiff,.mp3,.wav,.ogg,.flac,.aac,.mp4,.avi,.mov,.webm,.mkv"
      />

      <div className="area-subida-icono">
        <CloudUpload />
      </div>

      <h2 className="area-subida-titulo">Suelta archivos aquí</h2>
      <p className="area-subida-texto">
        o{' '}
        <span
          className="area-subida-link"
          onClick={(e) => {
            e.stopPropagation();
            abrirSelector();
          }}
        >
          busca en tu dispositivo
        </span>
      </p>

      <div className="area-subida-formatos" onClick={(e) => e.stopPropagation()}>
        {FORMATOS_VISIBLES.map((formato) => (
          <BotonFormato
            key={formato.etiqueta}
            formato={formato}
            alSeleccionar={alSeleccionar}
          />
        ))}
      </div>

      {archivos.length > 0 && (
        <div className="area-subida-lista" onClick={(e) => e.stopPropagation()}>
          {archivos.map((archivo) => (
            <div key={archivo.id} className="archivo-item">
              <FileText size={20} style={{ color: 'var(--color-primario)', flexShrink: 0 }} />
              <div className="archivo-item-info">
                <div className="archivo-item-nombre">{archivo.nombre}</div>
                <div className="archivo-item-tamano">{formatearTamano(archivo.tamano)}</div>
              </div>
              {archivo.estado === 'error' && (
                <span className="archivo-item-estado error">{archivo.error}</span>
              )}
              <button
                className="archivo-item-eliminar"
                onClick={() => eliminarArchivo(archivo.id)}
                aria-label={`Eliminar ${archivo.nombre}`}
              >
                <X size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
