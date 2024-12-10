// PipelineConnection.tsx
import React, { useEffect, useState } from "react";
import { X } from "lucide-react"; // {{ edit_1 }}
import { Block } from "@/types/pipelineTypes";
import { calculateConnectionPoints } from "@/utils/pipelineUtils";

interface PipelineConnectionProps {
  id: string; // {{ edit_2 }}
  sourceBlock: Block;
  targetBlock: Block;
  sourceDimensions: { width: number; height: number };
  targetDimensions: { width: number; height: number };
  onDelete: () => void; // {{ edit_3 }}
}

export function PipelineConnection({
  id, // {{ edit_4 }}
  sourceBlock,
  targetBlock,
  sourceDimensions,
  targetDimensions,
  onDelete, // {{ edit_5 }}
}: PipelineConnectionProps) {
  const [pathData, setPathData] = useState<string>("");
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    if (!sourceBlock || !targetBlock || !sourceDimensions || !targetDimensions)
      return;

    const { sourceX, sourceY, targetX, targetY } = calculateConnectionPoints(
      sourceBlock,
      targetBlock,
      sourceDimensions,
      targetDimensions,
    );

    // Calculate the distance between source and target
    const dx = targetX - sourceX;
    const dy = targetY - sourceY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Adjust curvature based on distance
    const curvature = Math.min(0.2, 50 / distance); // Gentle curve, max 0.2

    // Calculate control points for the Bezier curve
    const controlPoint1X = sourceX + dx * curvature;
    const controlPoint1Y = sourceY + dy * 0.5;
    const controlPoint2X = targetX - dx * curvature;
    const controlPoint2Y = targetY - dy * 0.5;

    // Create the path data for the curved line
    const path = `M ${sourceX},${sourceY} C ${controlPoint1X},${controlPoint1Y} ${controlPoint2X},${controlPoint2Y} ${targetX},${targetY}`;

    setPathData(path);
  }, [sourceBlock, targetBlock, sourceDimensions, targetDimensions]);

  if (!pathData) return null;

  // Calculate midpoint for positioning the 'x' icon
  const [midX, midY] = calculateMidpoint(pathData);

  return (
    <svg
      className="absolute inset-0 pointer-events-none overflow-visible"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <defs>
        <marker
          id={`arrowhead-${sourceBlock.id}-${targetBlock.id}`}
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="black" />
        </marker>
      </defs>
      <path
        d={pathData}
        fill="none"
        stroke="black"
        strokeWidth="2"
        strokeDasharray="6,4" // Dotted line pattern
        markerEnd={`url(#arrowhead-${sourceBlock.id}-${targetBlock.id})`}
      />
      {isHovered && (
        <foreignObject x={midX - 10} y={midY - 10} width="20" height="20">
          <button
            onClick={onDelete}
            style={{
              background: "red",
              border: "none",
              borderRadius: "50%",
              cursor: "pointer",
              width: "20px",
              height: "20px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            title="Delete Connection"
            aria-label="Delete Connection"
          >
            <X size={12} color="white" />
          </button>
        </foreignObject>
      )}
    </svg>
  );
}

// {{ edit_6 }} Utility function to calculate midpoint from pathData
function calculateMidpoint(pathData: string): [number, number] {
  const pathParts = pathData.split(" ");
  const coordinates: number[] = [];

  pathParts.forEach((part) => {
    if (part.includes(",")) {
      const [x, y] = part.split(",").map(Number);
      coordinates.push(x, y);
    }
  });

  const midIndex = Math.floor(coordinates.length / 4) * 2;
  const midX = coordinates[midIndex];
  const midY = coordinates[midIndex + 1];

  return [midX, midY];
}
