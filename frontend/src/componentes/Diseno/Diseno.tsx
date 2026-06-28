import { Outlet } from 'react-router-dom';
import BarraNavegacion from '../BarraNavegacion/BarraNavegacion';
import PiePagina from '../PiePagina/PiePagina';
import './Diseno.css';

export default function Diseno() {
  return (
    <div className="diseno">
      <BarraNavegacion />
      <main className="diseno-contenido">
        <Outlet />
      </main>
      <PiePagina />
    </div>
  );
}
