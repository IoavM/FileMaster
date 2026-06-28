import { createBrowserRouter } from 'react-router-dom';
import Diseno from '../componentes/Diseno/Diseno';
import Inicio from '../paginas/Inicio/Inicio';
import Convertir from '../paginas/Convertir/Convertir';
import Herramientas from '../paginas/Herramientas/Herramientas';
import Historial from '../paginas/Historial/Historial';
import EditorPDF from '../paginas/EditorPDF/EditorPDF';
import GeneradorQR from '../paginas/GeneradorQR/GeneradorQR';
import TextoAVoz from '../paginas/TextoAVoz/TextoAVoz';
import DescargadorYouTube from '../paginas/DescargadorYouTube/DescargadorYouTube';
import EliminarFondo from '../paginas/EliminarFondo/EliminarFondo';
import CompresorImagenes from '../paginas/CompresorImagenes/CompresorImagenes';

const enrutador = createBrowserRouter([
  {
    path: '/',
    element: <Diseno />,
    children: [
      { index: true, element: <Inicio /> },
      { path: 'convertir', element: <Convertir /> },
      { path: 'herramientas', element: <Herramientas /> },
      { path: 'historial', element: <Historial /> },
      { path: 'herramientas/pdf', element: <EditorPDF /> },
      { path: 'herramientas/qr', element: <GeneradorQR /> },
      { path: 'herramientas/tts', element: <TextoAVoz /> },
      { path: 'herramientas/youtube', element: <DescargadorYouTube /> },
      { path: 'herramientas/fondo', element: <EliminarFondo /> },
      { path: 'herramientas/compresor', element: <CompresorImagenes /> },
    ],
  },
]);

export default enrutador;
