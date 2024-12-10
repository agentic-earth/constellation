"use client";

import React, { useContext, useEffect } from "react";
import { usePipelineSidebar } from "./usePipelineSidebar";
import { SidebarHeader } from "./SidebarHeader";
import { SidebarContent } from "./SidebarContent";
import { PipelineContext } from "@/contexts/PipelineContext";
import { BlockTypes } from "@/types/blockTypes";

export function PipelineSidebar() {
  const {
    activeTab,
    datasetBlocks,
    modelBlocks,
    handleTabChange,
    visibleItems,
    loadMoreItems,
    exportBlocks,
    setIsLoading,
    setExportBlocks,
    setDatasetBlocks,
    setModelBlocks,
  } = usePipelineSidebar();
  const context = useContext(PipelineContext);
  const allBlocks = context?.allBlocks || [];
  const isLoading = context?.isLoading || false;

  useEffect(() => {
    setDatasetBlocks(
      allBlocks.filter((block) => block.type === BlockTypes.DATASET),
    );
    setModelBlocks(
      allBlocks.filter((block) => block.type === BlockTypes.MODEL),
    );
    setExportBlocks(
      allBlocks.filter((block) => block.type === BlockTypes.EXPORT),
    );
  }, [allBlocks, setDatasetBlocks, setModelBlocks, setExportBlocks]);

  return (
    <div className="flex flex-col h-full bg-white rounded-3xl overflow-hidden shadow-lg w-full">
      <SidebarHeader activeTab={activeTab} onTabChange={handleTabChange} />

      <div className="mt-4">
        {" "}
        {/* Added vertical padding */}
        <SidebarContent
          activeTab={activeTab}
          isLoading={isLoading}
          datasetBlocks={datasetBlocks}
          modelBlocks={modelBlocks}
          visibleItems={visibleItems}
          onLoadMore={loadMoreItems}
          exportBlocks={exportBlocks}
        />
      </div>
    </div>
  );
}
