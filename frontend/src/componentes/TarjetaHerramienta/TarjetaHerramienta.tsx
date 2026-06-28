import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import type { Herramienta } from '../../interfaces/tipos';
import './TarjetaHerramienta.css';

interface PropiedadesTarjeta {
  herramienta: Herramienta;
  Icono: React.ElementType;
}

export default function TarjetaHerramienta({ herramienta, Icono }: PropiedadesTarjeta) {
  return (
    <Link to={herramienta.ruta} className="tarjeta-herramienta" id={`herramienta-${herramienta.id}`}>
      <div
        className="tarjeta-herramienta-icono"
        style={{ background: herramienta.color + '20', color: herramienta.color }}
      >
        <Icono />
      </div>
      <h3 className="tarjeta-herramienta-titulo">{herramienta.titulo}</h3>
      <p className="tarjeta-herramienta-descripcion">{herramienta.descripcion}</p>
      <span className="tarjeta-herramienta-enlace">
        Usar herramienta <ArrowRight size={14} />
      </span>
    </Link>
  );
}
