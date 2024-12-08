import { useState, useCallback } from 'react';

export function useZooming() {
  const [zoomLevel, setZoomLevel] = useState(1);

  const handleZoomIn = useCallback(() => {
    setZoomLevel((prev) => Math.min(prev + 0.1, 3));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoomLevel((prev) => Math.max(prev - 0.1, 0.5));
  }, []);

  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      if (e.ctrlKey) {
        e.preventDefault();
        if (e.deltaY < 0) {
          handleZoomIn();
        } else {
          handleZoomOut();
        }
      }
    },
    [handleZoomIn, handleZoomOut]
  );

  return { zoomLevel, handleZoomIn, handleZoomOut, handleWheel };
}