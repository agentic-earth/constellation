import React from "react";
import { ScrollArea } from "@/components/ui";
import { Loader2 } from "lucide-react";
import { DraggableBlock } from "./DraggableBlock";
import { BlockTypes, BlockType } from "@/types/blockTypes";

interface SidebarContentProps {
  activeTab: BlockType;
  isLoading: boolean;
  datasetBlocks: any[];
  modelBlocks: any[];
  visibleItems: number;
  onLoadMore: () => void;
  exportBlocks: any[];
}

export function SidebarContent({
  activeTab,
  isLoading,
  datasetBlocks,
  modelBlocks,
  visibleItems,
  onLoadMore,
  exportBlocks,
}: SidebarContentProps) {
  const visibleBlocks =
    activeTab === BlockTypes.DATASET
      ? datasetBlocks.slice(0, visibleItems)
      : activeTab === BlockTypes.MODEL
      ? modelBlocks.slice(0, visibleItems)
      : exportBlocks.slice(0, visibleItems);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const bottom =
      e.currentTarget.scrollHeight - e.currentTarget.scrollTop ===
      e.currentTarget.clientHeight;
    if (bottom && !isLoading) {
      onLoadMore();
    }
  };

  return (
    <div className="flex-grow overflow-hidden px-4 sm:px-6">
      <ScrollArea
        className="h-[calc(100vh-300px)]"
        onScrollCapture={handleScroll}
      >
        {isLoading && (
          <div className="flex items-center justify-center h-20">
            <Loader2 className="w-6 h-6 animate-spin text-gray-500" />
          </div>
        )}
        {!isLoading &&
          visibleBlocks.map((block) => (
            <DraggableBlock key={block.id} block={block} />
          ))}
        {visibleBlocks.length === 0 && !isLoading && (
          <p className="text-sm text-gray-500 mt-4">
            No{" "}
            {activeTab === BlockTypes.DATASET
              ? "datasets"
              : activeTab === BlockTypes.MODEL
              ? "models"
              : "exports"}{" "}
            found.
          </p>
        )}
      </ScrollArea>
    </div>
  );
}
