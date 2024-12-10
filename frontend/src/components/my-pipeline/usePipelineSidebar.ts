import { useState, useEffect, useCallback } from "react";
import { SatelliteSource, FullPaper, PaperType } from "@/types/paperTypes";
import { BlockTypes, BlockType } from "@/types/blockTypes";

export function usePipelineSidebar() {
  const [activeTab, setActiveTab] = useState<BlockType>(BlockTypes.DATASET);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDataSources, setSelectedDataSources] = useState<string[]>([]);
  const [allDataSources] = useState<string[]>(Object.values(SatelliteSource));
  const [isDataSourceFilterCollapsed, setIsDataSourceFilterCollapsed] =
    useState(false);
  const [datasetBlocks, setDatasetBlocks] = useState<any[]>([]);
  const [modelBlocks, setModelBlocks] = useState<any[]>([]);
  const [exportBlocks, setExportBlocks] = useState<any[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [visibleItems, setVisibleItems] = useState(10);

  const handleTabChange = useCallback((value: BlockType) => {
    setActiveTab(value);
    setSelectedDataSources([]);
    setSearchTerm("");
    setVisibleItems(10);
  }, []);

  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setSearchTerm(e.target.value);
    },
    [],
  );

  const loadMoreItems = useCallback(() => {
    setVisibleItems((prev) => prev + 10);
  }, []);

  return {
    activeTab,
    searchTerm,
    isLoading,
    selectedDataSources,
    allDataSources,
    isDataSourceFilterCollapsed,
    datasetBlocks,
    modelBlocks,
    exportBlocks,
    totalCount,
    handleTabChange,
    handleSearchChange,
    setSelectedDataSources,
    setIsDataSourceFilterCollapsed,
    visibleItems,
    loadMoreItems,
    setIsLoading,
    setExportBlocks,
    setDatasetBlocks,
    setModelBlocks,
  };
}
