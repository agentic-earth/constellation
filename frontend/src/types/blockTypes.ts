export const BlockTypes = {
  MODEL: "model",
  DATASET: "dataset",
  EXPORT: "exports",
} as const;

export type BlockType = (typeof BlockTypes)[keyof typeof BlockTypes];

export interface Block {
  id: string;
  name: string;
  type: BlockType;
  dataSources: string[];
  position: { x: number; y: number };
}

export interface DatasetBlock extends Block {
  filepath: string;
}
