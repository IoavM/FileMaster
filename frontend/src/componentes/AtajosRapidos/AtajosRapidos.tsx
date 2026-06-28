import { Link } from 'react-router-dom';
import {
  FileText,
  FileImage,
  FileSpreadsheet,
  Merge,
  ChevronRight,
} from 'lucide-react';
import './AtajosRapidos.css';

const ATAJOS = [
  {
    id: 'pdf-a-word',
    titulo: 'PDF a Word',
    icono: FileText,
    colorFondo: '#FEE2E2',
    colorIcono: '#DC2626',
    ruta: '/convertir?de=pdf&a=docx',
  },
  {
    id: 'jpg-a-pdf',
    titulo: 'JPG a PDF',
    icono: FileImage,
    colorFondo: '#FEF3C7',
    colorIcono: '#F59E0B',
    ruta: '/convertir?de=jpg&a=pdf',
  },
  {
    id: 'excel-a-pdf',
    titulo: 'Excel a PDF',
    icono: FileSpreadsheet,
    colorFondo: '#DCFCE7',
    colorIcono: '#16A34A',
    ruta: '/convertir?de=xlsx&a=pdf',
  },
  {
    id: 'unir-pdf',
    titulo: 'Unir PDF',
    icono: Merge,
    colorFondo: '#DBEAFE',
    colorIcono: '#2563EB',
    ruta: '/herramientas/pdf?op=unir',
  },
];

export default function AtajosRapidos() {
  return (
    <div className="atajos-panel" id="atajos-rapidos">
      <p className="atajos-titulo">Atajos Rápidos</p>

      <div className="atajos-lista">
        {ATAJOS.map((atajo) => (
          <Link key={atajo.id} to={atajo.ruta} className="atajo-item">
            <div
              className="atajo-icono"
              style={{ background: atajo.colorFondo }}
            >
              <atajo.icono style={{ color: atajo.colorIcono }} />
            </div>
            <span className="atajo-texto">{atajo.titulo}</span>
            <ChevronRight size={18} className="atajo-flecha" />
          </Link>
        ))}
      </div>
    </div>
  );
}
