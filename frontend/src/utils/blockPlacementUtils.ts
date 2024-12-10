import { BlockTypes, BlockType } from "@/types/blockTypes";
import { Block } from "@/types/pipelineTypes";

const GRID_SIZE_X = 300;
const GRID_SIZE_Y = 250; // Increased vertical spacing
const DATASET_X = 100;
const MODEL_START_X = 400;
const VERTICAL_OFFSET = 450; // Added vertical offset to move blocks down

export function calculatePosition(
  index: number,
  totalBlocks: number,
  type: BlockType,
  blockDimensions: { width: number; height: number },
): { x: number; y: number } {
  if (type === BlockTypes.DATASET) {
    return {
      x: DATASET_X,
      y: index * GRID_SIZE_Y + VERTICAL_OFFSET,
    };
  } else {
    const modelIndex = index - Math.floor(totalBlocks / 2); // Assuming half are datasets
    const column = Math.floor(modelIndex / 2);
    const row = modelIndex % 2;
    const x = MODEL_START_X + column * GRID_SIZE_X;
    const y =
      row * GRID_SIZE_Y + VERTICAL_OFFSET + (column % 2) * (GRID_SIZE_Y / 2);

    // Add some randomness to prevent perfect alignment
    return {
      x: x + (Math.random() * 40 - 20),
      y: y + (Math.random() * 40 - 20),
    };
  }
}

// {{ edit_2 }} New function to calculate connection points on block perimeters
export function calculateConnectionPoints(
  sourceBlock: Block,
  targetBlock: Block,
  sourceDimensions: { width: number; height: number },
  targetDimensions: { width: number; height: number },
): { sourceX: number; sourceY: number; targetX: number; targetY: number } {
  // Determine centers of source and target blocks
  const sourceCenterX = sourceBlock.position.x + sourceDimensions.width / 2;
  const sourceCenterY = sourceBlock.position.y + sourceDimensions.height / 2;
  const targetCenterX = targetBlock.position.x + targetDimensions.width / 2;
  const targetCenterY = targetBlock.position.y + targetDimensions.height / 2;

  // Calculate the angle between source and target centers
  const angle = Math.atan2(
    targetCenterY - sourceCenterY,
    targetCenterX - sourceCenterX,
  );

  // Calculate points on the perimeter based on angle
  const sourceOffsetX = (sourceDimensions.width / 2) * Math.cos(angle);
  const sourceOffsetY = (sourceDimensions.height / 2) * Math.sin(angle);
  const targetOffsetX =
    (targetDimensions.width / 2) * Math.cos(angle + Math.PI);
  const targetOffsetY =
    (targetDimensions.height / 2) * Math.sin(angle + Math.PI);

  return {
    sourceX: sourceCenterX + sourceOffsetX,
    sourceY: sourceCenterY + sourceOffsetY,
    targetX: targetCenterX + targetOffsetX,
    targetY: targetCenterY + targetOffsetY,
  };
}
