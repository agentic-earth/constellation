import React, { useEffect, useState } from "react";
import { Globe, Loader2, RefreshCw, Edit, ChevronDown } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"; // Example Shadcn components
import {
  clearPipelines,
  getPipelineRuns,
  runPipeline,
} from "@/services/pipelineService";
import { PipelineRun } from "@/types/pipelineTypes";
import { toast } from "@/hooks/use-toast";
import { usePipelineContext } from "@/contexts/PipelineContext";
import { parseDagsterConfigToBlocks } from "@/services/blockService";

function capitalizeFirstLetter(string: string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export default function PipelineList() {
  const {
    setIsListView,
    setBlocks,
    setConnections,
    setDagsterConfig,
    allBlocks,
  } = usePipelineContext();
  const [isLoading, setIsLoading] = useState(true);
  const [pipelines, setPipelines] = useState<PipelineRun[]>([]);
  const [expandedPipelineId, setExpandedPipelineId] = useState<string | null>(
    null
  );

  const fetchPipelines = () => {
    setIsLoading(true);
    getPipelineRuns()
      .then(setPipelines)
      .finally(() => setIsLoading(false));
  };

  const handleClearPipelines = (pipelineIds: string[]) => {
    clearPipelines(pipelineIds);
    setPipelines([]);
    fetchPipelines();
  };

  const handleReRun = async (pipelineId: string) => {
    const pipeline = pipelines.find((p) => p.id === pipelineId);
    const config = pipeline?.config;
    if (!config) {
      toast({
        title: "No config found",
        description: "Please try again later",
        variant: "destructive",
      });
      return;
    }

    const deployData = await runPipeline(config);

    if (deployData) {
      toast({
        title: "Deployment Successful",
        description: "Your pipeline has been deployed.",
        variant: "default",
      });
    }

    fetchPipelines();
  };

  const handleEdit = (pipelineId: string) => {
    const pipeline = pipelines.find((p) => p.id === pipelineId);
    const config = pipeline?.config;
    if (!config) {
      toast({
        title: "No config found",
        description: "Please try again later",
        variant: "destructive",
      });
      return;
    }

    setBlocks([]);
    setConnections([]);
    setDagsterConfig(config);
    parseDagsterConfigToBlocks(config, allBlocks, setBlocks, setConnections);
    setIsListView(false);
  };

  const toggleExpand = (pipelineId: string) => {
    setExpandedPipelineId((prevId) =>
      prevId === pipelineId ? null : pipelineId
    );
  };

  useEffect(() => {
    fetchPipelines();
    const intervalId = setInterval(fetchPipelines, 30000); // Refresh every 5 seconds

    return () => clearInterval(intervalId); // Cleanup interval on component unmount
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex space-x-2">
        <button
          onClick={fetchPipelines}
          className="flex items-center justify-center p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors duration-200"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
        <button
          onClick={() =>
            handleClearPipelines(pipelines.map((p) => p.id.toString()))
          }
          className="flex items-center justify-center p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors duration-200"
        >
          Clear All
        </button>
      </div>
      {pipelines &&
        pipelines.length > 0 &&
        pipelines.map((pipeline) => (
          <Card
            key={pipeline.id}
            className={`mb-2 bg-white rounded-3xl shadow-sm hover:shadow-md transition-shadow duration-200`}
          >
            <CardContent className="p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Globe className="w-5 h-5 mr-2 text-blue-500" />
                  <p className="text-sm font-medium flex-1 line-clamp-1">
                    Run ID: {pipeline.runId}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleReRun(pipeline.id)}
                    className="flex items-center justify-center p-2 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors duration-200"
                  >
                    <RefreshCw className="w-4 h-4 text-gray-600" />
                  </button>
                  <button
                    onClick={() => handleEdit(pipeline.id)}
                    className="flex items-center justify-center p-2 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors duration-200"
                  >
                    <Edit className="w-4 h-4 text-gray-600" />
                  </button>
                  {pipeline.status === "failed" && (
                    <button
                      onClick={() => toggleExpand(pipeline.id)}
                      className="flex items-center justify-center p-2 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors duration-200"
                    >
                      <ChevronDown
                        className={`w-4 h-4 text-gray-600 ${
                          expandedPipelineId === pipeline.id ? "rotate-180" : ""
                        }`}
                      />
                    </button>
                  )}
                </div>
              </div>
              <span
                className={`text-sm ${
                  pipeline.status === "completed"
                    ? "text-green-500"
                    : pipeline.status === "running"
                    ? "text-yellow-500"
                    : "text-red-500"
                }`}
              >
                Status: {capitalizeFirstLetter(pipeline.status)}
              </span>
              {expandedPipelineId === pipeline.id &&
                pipeline.status === "failed" && (
                  <div className="mt-2 text-sm text-gray-500">
                    {pipeline.message || "No error message available."}
                  </div>
                )}
            </CardContent>
          </Card>
        ))}
      {!isLoading && (!pipelines || pipelines.length === 0) && (
        <p className="text-sm text-gray-500">No pipelines found</p>
      )}
      {isLoading && (
        <div className="flex justify-center items-center text-lg text-gray-500 mt-4">
          <Loader2 className="w-6 h-6 animate-spin text-gray-500 mr-2" />{" "}
          Loading...
        </div>
      )}
    </div>
  );
}
