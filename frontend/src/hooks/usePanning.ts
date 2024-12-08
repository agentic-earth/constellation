import { useState, useEffect, useCallback, RefObject } from "react";

export function usePanning(workspaceRef: React.RefObject<HTMLDivElement>) {
  const [isPanning, setIsPanning] = useState(false);
  const [start, setStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [scrollStart, setScrollStart] = useState<{ x: number; y: number }>({
    x: 0,
    y: 0,
  });

  const startPanning = useCallback(
    (e: React.MouseEvent) => {
      setIsPanning(true);
      setStart({ x: e.clientX, y: e.clientY });
      if (workspaceRef.current) {
        setScrollStart({
          x: workspaceRef.current.scrollLeft,
          y: workspaceRef.current.scrollTop,
        });
      }
    },
    [workspaceRef]
  );

  const pan = useCallback(
    (e: MouseEvent) => {
      if (!isPanning || !workspaceRef.current) return;
      const dx = e.clientX - start.x;
      const dy = e.clientY - start.y;
      workspaceRef.current.scrollLeft = scrollStart.x - dx;
      workspaceRef.current.scrollTop = scrollStart.y - dy;
    },
    [isPanning, start, scrollStart, workspaceRef]
  );

  const stopPanning = useCallback(() => {
    setIsPanning(false);
  }, []);

  return { isPanning, startPanning, stopPanning, pan };
}
