import React, { useRef, useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Trash2, Code, Save, Terminal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Rnd } from "react-rnd"; // Ensure you have react-rnd installed

interface PipelineRecapBlockProps {
  id: string;
  name: string;
  position: { x: number; y: number };
  onDelete: () => void;
}

export function PipelineRecapBlock({
  id,
  name,
  position,
  onDelete,
}: PipelineRecapBlockProps) {
  const blockRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 350, height: 250 });

  useEffect(() => {
    if (blockRef.current) {
      const rect = blockRef.current.getBoundingClientRect();
      setDimensions({ width: rect.width, height: rect.height });
    }
  }, []);

  return (
    <Rnd
      default={{
        x: position.x,
        y: position.y,
        width: dimensions.width,
        height: dimensions.height,
      }}
      bounds="parent"
      enableResizing={{
        top: true,
        right: true,
        bottom: true,
        left: true,
        topRight: true,
        bottomRight: true,
        bottomLeft: true,
        topLeft: true,
      }}
      onResizeStop={(e, direction, ref, delta, newPosition) => {
        setDimensions({
          width: ref.offsetWidth,
          height: ref.offsetHeight,
        });
      }}
      dragHandleClassName="drag-handle"
    >
      <div
        ref={blockRef}
        className="w-full h-full cursor-move"
        style={{ position: "relative" }}
      >
        <Card className="w-full h-full bg-purple-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-200">
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Pipeline Recap</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={onDelete}
                className="rounded-full p-1 hover:bg-gray-200 transition-colors"
                title="Delete Recap"
                aria-label="Delete Recap"
              >
                <Trash2 size={16} />
              </Button>
            </div>
            <div className="space-y-3 mb-4">
              <a
                href="https://placekitten.com/800/600"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center text-blue-600 hover:underline"
              >
                <Code className="w-4 h-4 mr-2" />
                Source Code
              </a>
              <a
                href="https://placekitten.com/800/600"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center text-green-600 hover:underline"
              >
                <Save className="w-4 h-4 mr-2" />
                Technical Write-Up
              </a>
              <a
                href="https://placekitten.com/800/600"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center text-yellow-600 hover:underline"
              >
                <Terminal className="w-4 h-4 mr-2" />
                How to Run
              </a>
            </div>
            <div>
              <p className="text-sm font-medium mb-1">Mock Docker Command:</p>
              <pre className="bg-gray-200 p-2 rounded text-xs overflow-auto">
                docker run -d -p 8080:80 your-pipeline-image:latest
              </pre>
            </div>
          </CardContent>
        </Card>
      </div>
    </Rnd>
  );
}
