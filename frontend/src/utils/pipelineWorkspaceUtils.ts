import { Block, Connection } from "@/types/pipelineTypes";
import { canConnect } from "./pipelineUtils";
import { v4 as uuidv4 } from "uuid";

export const handleBlockDrop = (
  item: Block,
  offset: { x: number; y: number },
  workspaceRect: DOMRect,
  scrollPosition: { x: number; y: number },
  zoomLevel: number
): Block => {
  const x = (offset.x - workspaceRect.left + scrollPosition.x) / zoomLevel;
  const y = (offset.y - workspaceRect.top + scrollPosition.y) / zoomLevel;
  return {
    ...item,
    position: { x, y },
    id: item.id || Date.now().toString(),
  };
};

export const handleBlockConnection = (
  selectedBlockId: string,
  targetBlockId: string,
  blocks: Block[],
  connections: Connection[]
): { newConnection: Connection | null; error: string | null } => {
  const sourceBlock = blocks.find((b) => b.id === selectedBlockId);
  const targetBlock = blocks.find((b) => b.id === targetBlockId);

  if (sourceBlock && targetBlock) {
    if (canConnect(sourceBlock, targetBlock)) {
      return {
        newConnection: {
          id: uuidv4(),
          source: selectedBlockId,
          target: targetBlockId,
        },
        error: null,
      };
    } else {
      return { newConnection: null, error: "Data sources do not match" };
    }
  }
  return { newConnection: null, error: "Invalid blocks" };
};

export const updateBlockPosition = (
  blocks: Block[],
  id: string,
  position: { x: number; y: number; width?: number; height?: number }
): Block[] => {
  return blocks.map((block) =>
    block.id === id ? { ...block, position: { ...position } } : block
  );
};

export const deleteBlock = (
  blocks: Block[],
  connections: Connection[],
  blockId: string
): { updatedBlocks: Block[]; updatedConnections: Connection[] } => {
  const updatedBlocks = blocks.filter((block) => block.id !== blockId);
  const updatedConnections = connections.filter(
    (connection) =>
      connection.source !== blockId && connection.target !== blockId
  );
  return { updatedBlocks, updatedConnections };
};

export const stopEventPropagation = (e: React.MouseEvent) => {
  e.stopPropagation();
};

export const calculateScaledPosition = (
  position: { x: number; y: number },
  zoomLevel: number
) => ({
  x: position.x * zoomLevel,
  y: position.y * zoomLevel,
});
