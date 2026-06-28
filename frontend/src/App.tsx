import { RouterProvider } from 'react-router-dom';
import enrutador from './rutas/Enrutador';

export default function App() {
  return <RouterProvider router={enrutador} />;
}
