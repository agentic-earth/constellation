// PipelineBlock.tsx
import React, { useRef, useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Globe,
  CloudRain,
  Database,
  Trash2,
  ChevronDown,
  ChevronUp,
  Download,
} from "lucide-react";
import { BlockType, BlockTypes } from "@/types/blockTypes";
import { SatelliteSource } from "@/types/paperTypes";
import { Button } from "@/components/ui/button";
import { PipelineBlockDropdown } from "./PipelineBlockDropdown";

interface PipelineBlockProps {
  id: string;
  name: string;
  type: BlockType;
  dataSources?: SatelliteSource[];
  position: { x: number; y: number };
  isSelected: boolean;
  onMouseDown: (e: React.MouseEvent) => void;
  onClick: (e: React.MouseEvent) => void;
  onDelete: () => void;
  onDimensionsChange: (id: string, width: number, height: number) => void;
}

export function PipelineBlock({
  id,
  name,
  type,
  dataSources = [],
  position,
  isSelected,
  onMouseDown,
  onClick,
  onDelete,
  onDimensionsChange,
}: PipelineBlockProps) {
  const blockRef = useRef<HTMLDivElement>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (blockRef.current) {
      const rect = blockRef.current.getBoundingClientRect();
      onDimensionsChange(id, rect.width, rect.height);
    }
  }, [blockRef, id, onDimensionsChange, isExpanded]);

  const renderIcon = () => {
    switch (type) {
      case BlockTypes.MODEL:
        return <CloudRain className="h-4 w-4 mr-1" />;
      case BlockTypes.DATASET:
        return <Database className="h-4 w-4 mr-1" />;
      case BlockTypes.EXPORT:
        return <Download className="h-4 w-4 mr-1" />;
      default:
        return <Globe className="h-4 w-4 mr-1" />;
    }
  };

  const toggleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded((prev) => !prev);
  };

  return (
    <div
      ref={blockRef}
      style={{
        position: "absolute",
        left: position.x,
        top: position.y,
        cursor: "move",
      }}
      onMouseDown={onMouseDown}
      onClick={onClick}
    >
      <Card
        className={`w-48 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-200 ${
          isSelected ? "ring-2 ring-blue-500" : ""
        }`}
      >
        <CardContent className="p-3 relative">
          {/* Trash Button Positioned at Upper Right */}
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="absolute top-1 right-1 rounded-full hover:bg-orange-100 hover:text-orange-600 transition-colors"
            aria-label="Delete"
          >
            <Trash2 size={16} />
          </Button>

          <Badge
            variant="secondary"
            className={`mb-2 ${
              type === BlockTypes.MODEL
                ? "bg-blue-100 text-blue-800"
                : "bg-green-100 text-green-800"
            }`}
          >
            {renderIcon()}
            {type}
          </Badge>
          <p className="text-sm font-medium">{name}</p>

          {/* Toggle Arrow Positioned at Bottom
          <div className="mt-auto mb-1 flex justify-center">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleExpand}
              className="p-0 w-6 h-6 rounded-full hover:bg-blue-200 transition-colors flex items-center justify-center"
              aria-label={isExpanded ? "Collapse" : "Expand"}
            >
              {isExpanded ? (
                <ChevronUp size={14} className="text-blue-600" />
              ) : (
                <ChevronDown size={14} className="text-blue-600" />
              )}
            </Button>
          </div> */}

          {/* Dropdown Content
          {isExpanded && (
            <div className="mt-1 overflow-hidden">
              <PipelineBlockDropdown type={type} />
            </div>
          )} */}
        </CardContent>
      </Card>
    </div>
  );
}
