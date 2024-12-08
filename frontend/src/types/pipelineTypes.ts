import { BlockType } from "./blockTypes";
import { SatelliteSource } from "./paperTypes";

export interface Block {
  id: string;
  name: string;
  type: BlockType;
  dataSources: SatelliteSource[];
  position: {
    x: number;
    y: number;
    width?: number;
    height?: number;
  };
}

export interface Connection {
  id: string;
  source: string;
  target: string;
}

export interface Operation {
  operation: string;
  parameters:
    | Record<string, number>
    | Record<string, Operation>
    | Record<string, string>;
}

export interface DagsterConfig {
  raw_input: Operation[];
}

export interface PipelineRun {
  id: string;
  runId: string;
  status: string;
  config: DagsterConfig;
  message: string;
}
