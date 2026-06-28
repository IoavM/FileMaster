import { useState, useCallback, useEffect } from 'react';
import type { ConversionReciente } from '../interfaces/tipos';

const CLAVE_HISTORIAL = 'filemaster_historial';

export function usarHistorial() {
  const [conversiones, establecerConversiones] = useState<ConversionReciente[]>([]);

  useEffect(() => {
    try {
      const datos = sessionStorage.getItem(CLAVE_HISTORIAL);
      if (datos) {
        establecerConversiones(JSON.parse(datos));
      }
    } catch {
      sessionStorage.removeItem(CLAVE_HISTORIAL);
    }
  }, []);

  const guardar = useCallback((lista: ConversionReciente[]) => {
    sessionStorage.setItem(CLAVE_HISTORIAL, JSON.stringify(lista));
    establecerConversiones(lista);
  }, []);

  const agregarConversion = useCallback((conversion: ConversionReciente) => {
    establecerConversiones((prev) => {
      const nueva = [conversion, ...prev].slice(0, 50); 
      sessionStorage.setItem(CLAVE_HISTORIAL, JSON.stringify(nueva));
      return nueva;
    });
  }, []);

  const actualizarConversion = useCallback((id: string, cambios: Partial<ConversionReciente>) => {
    establecerConversiones((prev) => {
      const actualizada = prev.map((c) => (c.id === id ? { ...c, ...cambios } : c));
      sessionStorage.setItem(CLAVE_HISTORIAL, JSON.stringify(actualizada));
      return actualizada;
    });
  }, []);

  const eliminarConversion = useCallback((id: string) => {
    establecerConversiones((prev) => {
      const filtrada = prev.filter((c) => c.id !== id);
      sessionStorage.setItem(CLAVE_HISTORIAL, JSON.stringify(filtrada));
      return filtrada;
    });
  }, []);

  const limpiarHistorial = useCallback(() => {
    guardar([]);
  }, [guardar]);

  return {
    conversiones,
    agregarConversion,
    actualizarConversion,
    eliminarConversion,
    limpiarHistorial,
  };
}
