import { Block, BlockTypes, DatasetBlock } from "@/types/blockTypes";
import { Operation } from "@/types/pipelineTypes";
import { DagsterConfig } from "@/types/pipelineTypes";
import { Connection } from "@/types/pipelineTypes";
import { Dispatch, SetStateAction } from "react";
const API_URL = `${process.env.NEXT_PUBLIC_API_URL}/blocks/get-all-blocks/?user_id=36906826-9558-4631-b4a6-c34d6109856d`;

export const getAllBlocks = async (toast) => {
  try {
    const response = await fetch(API_URL, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      toast({
        title: "Failed to fetch blocks",
        description: "Please try again later",
        variant: "destructive",
      });
      return [];
    }

    const data = await response.json();

    // Create block objects with the correct type
    const blocks = data.map((block: any) => ({
      ...block,
      type: block.block_type,
      filepath: block.filepath,
    }));

    return blocks;
  } catch (error) {
    toast({
      title: "Failed to fetch blocks",
      description: "Please try again later",
      variant: "destructive",
    });
    return [];
  }
};

export const parseDagsterConfigToBlocks = (
  dagsterConfig: DagsterConfig,
  allBlocks: Block[],
  setBlocks: Dispatch<SetStateAction<Block[]>>,
  setConnections: Dispatch<SetStateAction<Connection[]>>,
) => {
  const blocks: Block[] = [];
  const connections: Connection[] = [];

  const traverseDagsterConfig = (operation: Operation, parents: Block[]) => {
    let currentBlockId: string | undefined;

    if (operation.parameters) {
      for (const key in operation.parameters) {
        if (typeof operation.parameters[key] === "object") {
          traverseDagsterConfig(
            operation.parameters[key] as Operation,
            parents,
          );
        }
      }
    }

    // Add the block
    if (operation.operation == "import_from_google_drive") {
      const datasetName = operation.parameters.file_id;
      const datasetBlocks: DatasetBlock[] = allBlocks.filter(
        (block) => block.type === BlockTypes.DATASET,
      ) as DatasetBlock[];
      const datasetBlock: DatasetBlock | undefined = datasetBlocks.find(
        (block) => block.filepath === datasetName,
      );

      if (datasetBlock) {
        blocks.push(datasetBlock as Block);
        currentBlockId = datasetBlock.id;
        parents.push(datasetBlock as Block);
      }
    }

    if (operation.operation == "model_inference") {
      const modelName = operation.parameters.model;
      const modelBlock = allBlocks.find((block) => block.name === modelName);
      if (modelBlock) {
        blocks.push(modelBlock as Block);
        currentBlockId = modelBlock.id;
        parents.push(modelBlock as Block);
      }
    }

    if (operation.operation == "export_to_s3") {
      const exportToS3 = allBlocks.find(
        (block) => block.name === "export-to-S3",
      );
      if (exportToS3) {
        blocks.push(exportToS3 as Block);
        currentBlockId = exportToS3.id;
        parents.push(exportToS3 as Block);
      }
    }
  };

  // Recursively parse the dagster config to blocks and connections
  for (const operation of dagsterConfig.raw_input) {
    let parents: Block[] = [];
    traverseDagsterConfig(operation, parents);

    // Give parents unique ids with timestamp
    for (let i = 0; i < parents.length; i++) {
      parents[i].id = `${Date.now()}-${i}`;
    }

    // Add conenctions from left to right
    for (let i = 0; i < parents.length - 1; i++) {
      connections.push({
        source: parents[i].id,
        target: parents[i + 1].id,
        id: "",
      });
    }

    parents = [];
  }

  // Give blocks position
  for (let i = 0; i < blocks.length; i++) {
    blocks[i].position = { x: 50, y: i * 125 + 50 };
  }

  setBlocks(blocks);
  setConnections(connections);
};
