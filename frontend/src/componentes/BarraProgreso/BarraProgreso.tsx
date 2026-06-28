import type { EstadoConversion } from '../../interfaces/tipos';
import './BarraProgreso.css';

interface PropiedadesBarra {
  progreso: number;
  estado?: EstadoConversion;
  etiqueta?: string;
  mostrarPorcentaje?: boolean;
}

export default function BarraProgreso({
  progreso,
  estado = 'subiendo',
  etiqueta,
  mostrarPorcentaje = true,
}: PropiedadesBarra) {
  const claseEstado =
    estado === 'completado' ? 'completado' :
    estado === 'error' ? 'error' : '';

  return (
    <div className="barra-progreso-contenedor">
      {(etiqueta || mostrarPorcentaje) && (
        <div className="barra-progreso-info">
          {etiqueta && <span className="barra-progreso-etiqueta">{etiqueta}</span>}
          {mostrarPorcentaje && (
            <span className="barra-progreso-porcentaje">{Math.round(progreso)}%</span>
          )}
        </div>
      )}
      <div className="barra-progreso">
        <div
          className={`barra-progreso-relleno ${claseEstado}`}
          style={{ width: `${Math.min(100, Math.max(0, progreso))}%` }}
        />
      </div>
    </div>
  );
}
