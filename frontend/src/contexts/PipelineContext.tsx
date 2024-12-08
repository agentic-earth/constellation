import { createContext, Dispatch, SetStateAction, useContext } from "react";
import { Block, Connection, DagsterConfig } from "@/types/pipelineTypes";

interface PipelineContextProps {
  blocks: Block[];
  setBlocks: Dispatch<SetStateAction<Block[]>>;
  connections: Connection[];
  setConnections: Dispatch<SetStateAction<Connection[]>>;
  dagsterConfig: DagsterConfig;
  setDagsterConfig: Dispatch<SetStateAction<DagsterConfig>>;
  allBlocks: Block[];
  setAllBlocks: Dispatch<SetStateAction<Block[]>>;
  isLoading: boolean;
  setIsLoading: Dispatch<SetStateAction<boolean>>;
  isListView: boolean;
  setIsListView: Dispatch<SetStateAction<boolean>>;
}

export const PipelineContext = createContext<PipelineContextProps | null>(null);

export const usePipelineContext = () => {
  const context = useContext(PipelineContext);
  if (!context) {
    throw new Error(
      "usePipelineContext must be used within a PipelineProvider"
    );
  }
  return context;
};
