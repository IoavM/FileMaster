import { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import './SelectorFormato.css';

interface PropiedadesSelector {
  formatos: string[];
  formatoSeleccionado: string;
  alSeleccionar: (formato: string) => void;
  placeholder?: string;
}

export default function SelectorFormato({
  formatos,
  formatoSeleccionado,
  alSeleccionar,
  placeholder = 'Seleccionar formato',
}: PropiedadesSelector) {
  const [abierto, establecerAbierto] = useState(false);
  const refContenedor = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function manejarClicFuera(evento: MouseEvent) {
      if (refContenedor.current && !refContenedor.current.contains(evento.target as Node)) {
        establecerAbierto(false);
      }
    }
    document.addEventListener('mousedown', manejarClicFuera);
    return () => document.removeEventListener('mousedown', manejarClicFuera);
  }, []);

  return (
    <div className="selector-formato" ref={refContenedor}>
      <button
        className={`selector-formato-btn ${abierto ? 'abierto' : ''}`}
        onClick={() => establecerAbierto(!abierto)}
        type="button"
      >
        {formatoSeleccionado
          ? formatoSeleccionado.toUpperCase()
          : placeholder}
        <ChevronDown size={16} className="selector-formato-flecha" />
      </button>

      {abierto && (
        <div className="selector-formato-lista">
          {formatos.map((formato) => (
            <button
              key={formato}
              className={`selector-formato-opcion ${formato === formatoSeleccionado ? 'seleccionado' : ''}`}
              onClick={() => {
                alSeleccionar(formato);
                establecerAbierto(false);
              }}
              type="button"
            >
              {formato.toUpperCase()}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
