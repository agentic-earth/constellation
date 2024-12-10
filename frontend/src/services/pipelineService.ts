import { DagsterConfig } from "@/types/pipelineTypes";
import { toast } from "@/hooks/use-toast";

const API_URL = `${process.env.NEXT_PUBLIC_API_URL}`;

export const createGeneratedPipeline = async (query: string) => {
  try {
    const response = await fetch(
      `${API_URL}/blocks/construct-pipeline/?user_id=36906826-9558-4631-b4a6-c34d6109856d&query=${query}`,
      {
        method: "GET",
      },
    );

    const data = await response.json();

    return data;
  } catch (error) {
    toast({
      title: "Failed to create generated pipeline",
      description: "Please try again later",
      variant: "destructive",
    });
    return null;
  }
};

export const runPipeline = async (dagsterConfig: DagsterConfig) => {
  try {
    const response = await fetch(`${API_URL}/pipelines/run/`, {
      method: "POST",
      body: JSON.stringify({
        config: dagsterConfig.raw_input,
        user_id: "36906826-9558-4631-b4a6-c34d6109856d",
      }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    toast({
      title: "Failed to run pipeline",
      description: "Please try again later",
      variant: "destructive",
    });
    return null;
  }
};

export const getPipelineRuns = async () => {
  try {
    const response = await fetch(
      `${API_URL}/pipelines/?user_id=36906826-9558-4631-b4a6-c34d6109856d`,
    );
    const data = await response.json();

    // Create pipeline run objects with the correct type
    const pipelines = data.map((pipeline: any) => ({
      id: pipeline.pipeline_id,
      runId: pipeline.run_id,
      status: pipeline.status || "Unknown",
      config: { raw_input: pipeline.config } as DagsterConfig,
      message: pipeline.message || "No message available",
    }));

    return pipelines;
  } catch (error) {
    toast({
      title: "Failed to get pipeline runs",
      description: "Please try again later",
      variant: "destructive",
    });
  }
};

export const clearPipelines = async (pipelineIds: string[]) => {
  try {
    for (const pipelineId of pipelineIds) {
      console.log(pipelineId);
      const response = await fetch(
        `${API_URL}/pipelines/${pipelineId}/?user_id=36906826-9558-4631-b4a6-c34d6109856d`,
        {
          method: "DELETE",
        },
      );
    }
  } catch (error) {
    toast({
      title: "Failed to clear pipelines",
      description: "Please try again later",
      variant: "destructive",
    });
  }
};
