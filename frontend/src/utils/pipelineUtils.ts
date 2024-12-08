// File: src/utils/pipelineUtils.ts

import { Block } from "@/types/pipelineTypes";
import { BlockTypes } from "@/types/blockTypes";

interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface Point {
  x: number;
  y: number;
}

export function getClosestPointOnRect(rect: Rect, point: Point): Point {
  const x = Math.max(rect.x, Math.min(point.x, rect.x + rect.width));
  const y = Math.max(rect.y, Math.min(point.y, rect.y + rect.height));

  if (
    point.x >= rect.x &&
    point.x <= rect.x + rect.width &&
    point.y >= rect.y &&
    point.y <= rect.y + rect.height
  ) {
    const distances = [
      { x: point.x, y: rect.y, dist: Math.abs(point.y - rect.y) },
      {
        x: point.x,
        y: rect.y + rect.height,
        dist: Math.abs(point.y - (rect.y + rect.height)),
      },
      { x: rect.x, y: point.y, dist: Math.abs(point.x - rect.x) },
      {
        x: rect.x + rect.width,
        y: point.y,
        dist: Math.abs(point.x - (rect.x + rect.width)),
      },
    ];
    distances.sort((a, b) => a.dist - b.dist);
    return { x: distances[0].x, y: distances[0].y };
  }

  return { x, y };
}

// Function to determine if two blocks can be connected
export function canConnect(sourceBlock: Block, targetBlock: Block): boolean {
  // Prevent connecting blocks of the same type
  if (sourceBlock.type === targetBlock.type) {
    return false;
  }

  // Ensure dataset is always the source and model is always the target
  if (
    sourceBlock.type === BlockTypes.DATASET &&
    targetBlock.type === BlockTypes.MODEL
  ) {
    return sourceBlock.dataSources.some((source) =>
      targetBlock.dataSources.includes(source)
    );
  }

  return false;
}

// utils/pipelineUtils.ts
export function calculateConnectionPoints(
  sourceBlock,
  targetBlock,
  sourceDimensions,
  targetDimensions
) {
  // Get positions and sizes
  const sourceX = sourceBlock.position.x;
  const sourceY = sourceBlock.position.y;
  const sourceWidth = sourceDimensions?.width || 192; // Default width if dimensions are not available
  const sourceHeight = sourceDimensions?.height || 100; // Default height

  const targetX = targetBlock.position.x;
  const targetY = targetBlock.position.y;
  const targetWidth = targetDimensions?.width || 192;
  const targetHeight = targetDimensions?.height || 100;

  // Centers of the blocks
  const sourceCenterX = sourceX + sourceWidth / 2;
  const sourceCenterY = sourceY + sourceHeight / 2;

  const targetCenterX = targetX + targetWidth / 2;
  const targetCenterY = targetY + targetHeight / 2;

  // Calculate the vector from source to target
  const dx = targetCenterX - sourceCenterX;
  const dy = targetCenterY - sourceCenterY;

  // Determine the side of the source block where the connection should start
  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);

  let sourceEdgeX, sourceEdgeY;
  let targetEdgeX, targetEdgeY;

  if (absDx > absDy) {
    // Connect from left or right side
    sourceEdgeX = dx > 0 ? sourceX + sourceWidth : sourceX;
    sourceEdgeY = sourceCenterY;

    targetEdgeX = dx > 0 ? targetX : targetX + targetWidth;
    targetEdgeY = targetCenterY;
  } else {
    // Connect from top or bottom side
    sourceEdgeX = sourceCenterX;
    sourceEdgeY = dy > 0 ? sourceY + sourceHeight : sourceY;

    targetEdgeX = targetCenterX;
    targetEdgeY = dy > 0 ? targetY : targetY + targetHeight;
  }

  return {
    sourceX: sourceEdgeX,
    sourceY: sourceEdgeY,
    targetX: targetEdgeX,
    targetY: targetEdgeY,
  };
}
