import TablaConversiones from '../../componentes/TablaConversiones/TablaConversiones';
import { usarHistorial } from '../../hooks/usarHistorial';

export default function Historial() {
  const { conversiones, limpiarHistorial } = usarHistorial();

  return (
    <div className="contenedor">
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, color: 'var(--color-neutro)', marginBottom: 8 }}>
          Historial de Conversiones
        </h1>
        <p style={{ fontSize: 15, color: 'var(--color-secundario)' }}>
          Tu historial de conversiones de esta sesión. Se borra al cerrar el navegador.
        </p>
      </div>

      <TablaConversiones
        conversiones={conversiones}
        alLimpiar={limpiarHistorial}
      />
    </div>
  );
}
