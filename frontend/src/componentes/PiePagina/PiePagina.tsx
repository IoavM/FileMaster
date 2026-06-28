import { Link } from 'react-router-dom';
import './PiePagina.css';

export default function PiePagina() {
  const anio = new Date().getFullYear();

  return (
    <footer className="pie-pagina" id="pie-pagina">
      <div className="contenedor">
        <p className="pie-pagina-texto">
          © {anio} FileMaster. Todas las herramientas son gratuitas.
        </p>
        <nav className="pie-pagina-enlaces">
          <Link to="/herramientas" className="pie-pagina-enlace">
            Herramientas
          </Link>
          <Link to="/" className="pie-pagina-enlace">
            Convertir
          </Link>
          <Link to="/historial" className="pie-pagina-enlace">
            Historial
          </Link>
        </nav>
      </div>
    </footer>
  );
}
