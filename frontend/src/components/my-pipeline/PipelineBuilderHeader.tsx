import React, { useContext, useState } from "react";
import { PipelineContext } from "@/contexts/PipelineContext";
import { PipelineDescription } from "./PipelineDescription";
import { QueryInput } from "./QueryInput";
import { DagsterConfig } from "@/types/pipelineTypes";
import { createGeneratedPipeline } from "@/services/pipelineService";
import { parseDagsterConfigToBlocks } from "@/services/blockService";

export function PipelineBuilderHeader() {
  const { setBlocks, setConnections, setDagsterConfig, allBlocks } =
    useContext(PipelineContext)!;
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setIsLoading(true);

    const data = await createGeneratedPipeline(query);

    // Check for pipeline config
    if (data && data.pipeline.ops.generate_dynamic_job_configs.config) {
      setBlocks([]);
      setConnections([]);
      const dagsterConfig: DagsterConfig =
        data.pipeline.ops.generate_dynamic_job_configs.config;
      setDagsterConfig(dagsterConfig);
      parseDagsterConfigToBlocks(
        dagsterConfig,
        allBlocks,
        setBlocks,
        setConnections
      );
    }

    setIsLoading(false);
  };

  return (
    <section className="w-full py-8 md:py-12 bg-gradient-to-br from-primary to-primary/90">
      <div className="container mx-auto px-4 md:px-6 space-y-6">
        <div className="flex flex-col md:flex-row items-stretch gap-6">
          <PipelineDescription>
            <QueryInput
              query={query}
              setQuery={setQuery}
              handleSubmit={handleSubmit}
              isLoading={isLoading}
            />
          </PipelineDescription>
        </div>
      </div>
    </section>
  );
}
