import {
  FileOutput,
  FileText,
  QrCode,
  Volume2,
  Play,
  Eraser,
  ImageDown,
} from 'lucide-react';
import TarjetaHerramienta from '../../componentes/TarjetaHerramienta/TarjetaHerramienta';
import type { Herramienta } from '../../interfaces/tipos';
import './Herramientas.css';

const HERRAMIENTAS: { datos: Herramienta; icono: React.ElementType }[] = [
  {
    datos: {
      id: 'convertir',
      titulo: 'Convertir Archivos',
      descripcion: 'Convierte documentos, imágenes, audio y video entre múltiples formatos.',
      icono: 'FileOutput',
      categoria: 'conversion',
      ruta: '/',
      color: '#2563EB',
    },
    icono: FileOutput,
  },
  {
    datos: {
      id: 'editor-pdf',
      titulo: 'Editor PDF',
      descripcion: 'Unir, dividir, comprimir y rotar archivos PDF fácilmente.',
      icono: 'FileText',
      categoria: 'pdf',
      ruta: '/herramientas/pdf',
      color: '#DC2626',
    },
    icono: FileText,
  },
  {
    datos: {
      id: 'generador-qr',
      titulo: 'Generador QR',
      descripcion: 'Genera códigos QR personalizados para URLs, textos y más.',
      icono: 'QrCode',
      categoria: 'utilidad',
      ruta: '/herramientas/qr',
      color: '#0F172A',
    },
    icono: QrCode,
  },
  {
    datos: {
      id: 'texto-a-voz',
      titulo: 'Texto a Voz',
      descripcion: 'Convierte cualquier texto en audio con voces naturales en español.',
      icono: 'Volume2',
      categoria: 'audio',
      ruta: '/herramientas/tts',
      color: '#7C3AED',
    },
    icono: Volume2,
  },
  {
    datos: {
      id: 'descargador-youtube',
      titulo: 'Descargador YouTube',
      descripcion: 'Descarga videos y audio de YouTube en la mejor calidad disponible.',
      icono: 'Play',
      categoria: 'video',
      ruta: '/herramientas/youtube',
      color: '#DC2626',
    },
    icono: Play,
  },
  {
    datos: {
      id: 'eliminar-fondo',
      titulo: 'Eliminar Fondo',
      descripcion: 'Remueve el fondo de cualquier imagen de forma automática e inteligente.',
      icono: 'Eraser',
      categoria: 'imagen',
      ruta: '/herramientas/fondo',
      color: '#16A34A',
    },
    icono: Eraser,
  },
  {
    datos: {
      id: 'compresor-imagenes',
      titulo: 'Comprimir Imágenes',
      descripcion: 'Reduce el tamaño de tus imágenes sin perder calidad visual.',
      icono: 'ImageDown',
      categoria: 'imagen',
      ruta: '/herramientas/compresor',
      color: '#F59E0B',
    },
    icono: ImageDown,
  },
];

export default function Herramientas() {
  return (
    <div className="herramientas">
      <div className="contenedor">
        {}
        <div className="herramientas-encabezado">
          <h1 className="herramientas-titulo">Todas las Herramientas</h1>
          <p className="herramientas-subtitulo">
            Herramientas gratuitas para convertir, editar y transformar tus archivos sin límites.
          </p>
        </div>

        {}
        <div className="herramientas-grid">
          {HERRAMIENTAS.map((herramienta) => (
            <TarjetaHerramienta
              key={herramienta.datos.id}
              herramienta={herramienta.datos}
              Icono={herramienta.icono}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
