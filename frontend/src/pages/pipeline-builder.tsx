"use client";

import React, { useState, useCallback, useEffect } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { NavBar } from "@/components/home/NavBar";
import { Footer } from "@/components/home/Footer";
import { PipelineSidebar } from "@/components/my-pipeline/PipelineSidebar";
import { PipelineWorkspace } from "@/components/my-pipeline/PipelineWorkspace";
import { PipelineBuilderHeader } from "@/components/my-pipeline/PipelineBuilderHeader";
import { Toaster } from "@/components/ui/toaster";
import { PipelineContext } from "@/contexts/PipelineContext";
import { Block, Connection, DagsterConfig } from "@/types/pipelineTypes";
import { getAllBlocks } from "@/services/blockService";
import { Button } from "@/components/ui/button";
import PipelineList from "@/components/my-pipeline/PipelineList";
import { toast } from "@/hooks/use-toast";

export default function PipelineBuilder() {
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [dagsterConfig, setDagsterConfig] = useState<DagsterConfig>({
    raw_input: [],
  });
  const [allBlocks, setAllBlocks] = useState<Block[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isListView, setIsListView] = useState<boolean>(false);

  const handleClearAll = useCallback(() => {
    setBlocks([]);
    setConnections([]);
  }, []);

  const toggleView = useCallback(() => {
    setIsListView((prev) => !prev);
  }, []);

  useEffect(() => {
    const fetchAllBlocks = async () => {
      setIsLoading(true);
      const data = await getAllBlocks(toast);
      setAllBlocks(data);
      setIsLoading(false);
    };
    fetchAllBlocks();
  }, []);

  return (
    <DndProvider backend={HTML5Backend}>
      <PipelineContext.Provider
        value={{
          blocks,
          setBlocks,
          connections,
          setConnections,
          dagsterConfig,
          setDagsterConfig,
          allBlocks,
          setAllBlocks,
          isLoading,
          setIsLoading,
          isListView,
          setIsListView,
        }}
      >
        <div className="flex flex-col min-h-screen bg-gray-50">
          <NavBar />
          <main className="flex-1 flex flex-col">
            <PipelineBuilderHeader />
            <div className="flex flex-1 flex-col md:flex-row p-4 md:p-6 gap-4">
              <div className="w-full md:w-1/4 bg-white rounded-3xl shadow-lg overflow-hidden min-w-[400px]">
                <PipelineSidebar />
              </div>
              <div className="flex-1 relative">
                <Button
                  onClick={toggleView}
                  className="absolute bottom-4 left-4 z-20"
                >
                  {isListView
                    ? "Switch to Workspace View"
                    : "Switch to Pipeline Runs"}
                </Button>
                {isListView ? (
                  <div>
                    <PipelineList />
                  </div>
                ) : (
                  <PipelineWorkspace onClearAll={handleClearAll} />
                )}
              </div>
            </div>
          </main>

          <Footer />

          <Toaster />
        </div>
      </PipelineContext.Provider>
    </DndProvider>
  );
}
