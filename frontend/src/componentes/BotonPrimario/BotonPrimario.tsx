import type { ReactNode, ButtonHTMLAttributes } from 'react';
import type { VarianteBoton } from '../../interfaces/tipos';
import './BotonPrimario.css';

interface PropiedadesBoton extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: VarianteBoton;
  cargando?: boolean;
  icono?: ReactNode;
  children: ReactNode;
}

export default function BotonPrimario({
  variante = 'primario',
  cargando = false,
  icono,
  children,
  disabled,
  className = '',
  ...resto
}: PropiedadesBoton) {
  return (
    <button
      className={`boton boton-${variante} ${cargando ? 'boton-cargando' : ''} ${className}`}
      disabled={disabled || cargando}
      {...resto}
    >
      {cargando ? (
        <span className="boton-spinner" />
      ) : (
        icono
      )}
      {children}
    </button>
  );
}
