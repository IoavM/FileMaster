import { createBrowserRouter } from 'react-router-dom';
import Diseno from '../componentes/Diseno/Diseno';
import Inicio from '../paginas/Inicio/Inicio';
import Convertir from '../paginas/Convertir/Convertir';
import Herramientas from '../paginas/Herramientas/Herramientas';
import Historial from '../paginas/Historial/Historial';
import EditorPDF from '../paginas/EditorPDF/EditorPDF';
import GeneradorQR from '../paginas/GeneradorQR/GeneradorQR';
import TextoAVoz from '../paginas/TextoAVoz/TextoAVoz';

import CompresorImagenes from '../paginas/CompresorImagenes/CompresorImagenes';
import DetectorHumanizador from '../paginas/DetectorHumanizador/DetectorHumanizador';

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
      { path: 'herramientas/compresor', element: <CompresorImagenes /> },
      { path: 'herramientas/detector-ia', element: <DetectorHumanizador /> },
    ],
  },
]);

export default enrutador;

