import { History, Download, FileText, Inbox } from 'lucide-react';
import type { ConversionReciente } from '../../interfaces/tipos';
import { truncarNombre } from '../../utilidades/formateadores';
import './TablaConversiones.css';

interface PropiedadesTabla {
  conversiones: ConversionReciente[];
  alLimpiar: () => void;
}

const ETIQUETA_ESTADO: Record<string, string> = {
  completado: 'Completado',
  convirtiendo: 'En proceso',
  error: 'Error',
  pendiente: 'Pendiente',
  subiendo: 'Subiendo',
};

export default function TablaConversiones({ conversiones, alLimpiar }: PropiedadesTabla) {
  return (
    <div className="tabla-panel" id="tabla-conversiones">
      {}
      <div className="tabla-encabezado">
        <h2 className="tabla-titulo">
          <History size={20} className="tabla-titulo-icono" />
          Conversiones Recientes
        </h2>
        {conversiones.length > 0 && (
          <button className="tabla-limpiar" onClick={alLimpiar}>
            Limpiar todo
          </button>
        )}
      </div>

      {}
      {conversiones.length === 0 ? (
        <div className="tabla-vacia">
          <Inbox size={40} className="tabla-vacia-icono" />
          <p>No hay conversiones recientes</p>
        </div>
      ) : (
        <div className="tabla-contenedor">
          <table className="tabla">
            <thead>
              <tr>
                <th>Nombre Archivo</th>
                <th>Salida</th>
                <th>Tamaño</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {conversiones.map((conversion) => (
                <tr key={conversion.id}>
                  {}
                  <td>
                    <div className="tabla-nombre">
                      <FileText size={18} className="tabla-nombre-icono" style={{ color: '#DC2626' }} />
                      {truncarNombre(conversion.nombreArchivo)}
                    </div>
                  </td>

                  {}
                  <td>
                    <span className="tabla-formato">
                      {conversion.formatoSalida.toUpperCase()}
                    </span>
                  </td>

                  {}
                  <td>{conversion.tamano}</td>

                  {}
                  <td>
                    <span className={`tabla-estado ${conversion.estado}`}>
                      <span className="tabla-estado-punto" />
                      {ETIQUETA_ESTADO[conversion.estado] || conversion.estado}
                    </span>
                  </td>

                  {}
                  <td>
                    {conversion.estado === 'completado' && conversion.urlDescarga && (
                      <a
                        href={conversion.urlDescarga}
                        download
                        className="tabla-descarga"
                        aria-label={`Descargar ${conversion.nombreArchivo}`}
                      >
                        <Download size={18} />
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
