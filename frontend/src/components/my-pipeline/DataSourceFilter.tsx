import React from "react";
import { ToggleGroup, ToggleGroupItem, ScrollArea } from "@/components/ui";

interface DataSourceFilterProps {
  dataSourceOptions: string[];
  selectedDataSources: string[];
  setSelectedDataSources: React.Dispatch<React.SetStateAction<string[]>>;
  isCollapsed: boolean;
  setIsCollapsed: React.Dispatch<React.SetStateAction<boolean>>;
}

export const DataSourceFilter: React.FC<DataSourceFilterProps> = ({
  dataSourceOptions,
  selectedDataSources,
  setSelectedDataSources,
  isCollapsed,
  setIsCollapsed,
}) => {
  const handleDataSourceToggle = (value: string) => {
    setSelectedDataSources((prev) =>
      prev.includes(value)
        ? prev.filter((ds) => ds !== value)
        : [...prev, value],
    );
  };

  return (
    <div className="mt-4 mb-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-sm text-gray-500">
          Filter by Data Source
        </h3>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="text-sm text-blue-500 focus:outline-none"
        >
          {isCollapsed ? "Expand" : "Collapse"}
        </button>
      </div>
      {!isCollapsed && (
        <ScrollArea className="h-40 overflow-y-auto pr-4">
          <ToggleGroup
            type="multiple"
            value={selectedDataSources}
            onValueChange={setSelectedDataSources}
            className="flex flex-wrap gap-2"
          >
            {dataSourceOptions.map((source) => (
              <ToggleGroupItem
                key={source}
                value={source}
                aria-label={source}
                onClick={() => handleDataSourceToggle(source)}
                className="px-2 py-1 text-xs rounded-full"
              >
                {source}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </ScrollArea>
      )}
    </div>
  );
};
