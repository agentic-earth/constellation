import React from "react";
import { Button } from "@/components/ui/button";
import {
  Crosshair,
  Save,
  UploadCloud,
  Trash2,
  ZoomIn,
  ZoomOut,
  Maximize,
  Download,
} from "lucide-react";

interface PipelineWorkspaceControlsProps {
  onRecenter: () => void;
  onSave: () => void;
  onLoad: () => void;
  onClearAll: () => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onReset: () => void;
  onDownload: () => void;
  zoomLevel: number;
}

export function PipelineWorkspaceControls({
  onRecenter,
  onSave,
  onLoad,
  onClearAll,
  onZoomIn,
  onZoomOut,
  onReset,
  zoomLevel,
}: PipelineWorkspaceControlsProps) {
  return (
    <div className="absolute top-4 right-4 flex flex-col space-y-2 bg-white/80 backdrop-blur-sm p-2 rounded-xl shadow-lg">
      {/* Replace each Button component with this updated version */}
      <Button
        onClick={onZoomIn}
        className="rounded-full p-2 w-10 h-10 hover:bg-gray-200 transition-colors"
        variant="ghost"
        title="Zoom In"
      >
        <ZoomIn size={20} />
      </Button>
      <Button
        onClick={onZoomOut}
        className="rounded-full p-2 w-10 h-10 hover:bg-gray-200 transition-colors"
        variant="ghost"
        title="Zoom Out"
      >
        <ZoomOut size={20} />
      </Button>
      <Button
        onClick={onReset}
        className="rounded-full p-2 w-10 h-10 hover:bg-gray-200 transition-colors"
        variant="ghost"
        title="Reset Zoom"
      >
        <Maximize size={20} />
      </Button>
      <Button
        onClick={onClearAll}
        className="rounded-full p-2 w-10 h-10 hover:bg-gray-200 transition-colors"
        variant="ghost"
        title="Clear All"
      >
        <Trash2 size={20} />
      </Button>
      <div className="text-center text-sm font-medium">
        {(zoomLevel * 100).toFixed(0)}%
      </div>
    </div>
  );
}
