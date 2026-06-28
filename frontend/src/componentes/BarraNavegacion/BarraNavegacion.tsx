import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileOutput, Menu, X } from 'lucide-react';
import './BarraNavegacion.css';

const ENLACES = [
  { ruta: '/', etiqueta: 'Convertir' },
  { ruta: '/herramientas', etiqueta: 'Herramientas' },
  { ruta: '/historial', etiqueta: 'Historial' },
];

export default function BarraNavegacion() {
  const [menuAbierto, establecerMenuAbierto] = useState(false);
  const ubicacion = useLocation();

  const alternarMenu = () => establecerMenuAbierto(!menuAbierto);
  const cerrarMenu = () => establecerMenuAbierto(false);

  return (
    <nav className="barra-nav" id="barra-navegacion">
      <div className="contenedor">
        {}
        <Link to="/" className="nav-logo" onClick={cerrarMenu}>
          <FileOutput className="nav-logo-icono" />
          File<span>Master</span>
        </Link>

        {}
        <div className={`nav-enlaces ${menuAbierto ? 'abierto' : ''}`}>
          {ENLACES.map((enlace) => (
            <Link
              key={enlace.ruta}
              to={enlace.ruta}
              className={`nav-enlace ${ubicacion.pathname === enlace.ruta ? 'activo' : ''}`}
              onClick={cerrarMenu}
            >
              {enlace.etiqueta}
            </Link>
          ))}
        </div>

        {}
        <button
          className="nav-menu-btn"
          onClick={alternarMenu}
          aria-label={menuAbierto ? 'Cerrar menú' : 'Abrir menú'}
        >
          {menuAbierto ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
    </nav>
  );
}
