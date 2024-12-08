import React from "react";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui";
import { Satellite, CloudRain, Download } from "lucide-react";
import { BlockTypes, BlockType } from "@/types/blockTypes";

interface SidebarHeaderProps {
  activeTab: BlockType;
  onTabChange: (value: BlockType) => void;
}

export function SidebarHeader({ activeTab, onTabChange }: SidebarHeaderProps) {
  return (
    <div className="px-4 sm:px-6 pt-6">
      <div className="bg-gray-100 rounded-full p-1 shadow-sm mb-4">
        <ToggleGroup
          type="single"
          value={activeTab}
          onValueChange={onTabChange}
          className="flex flex-col sm:flex-row justify-between"
        >
          <ToggleGroupItem
            value={BlockTypes.DATASET}
            aria-label="Datasets"
            className="flex-1 rounded-full px-3 py-1 text-sm flex items-center justify-center"
          >
            <Satellite className="w-4 h-4 mr-1" />
            Datasets
          </ToggleGroupItem>
          <ToggleGroupItem
            value={BlockTypes.MODEL}
            aria-label="Models"
            className="flex-1 rounded-full px-3 py-1 text-sm flex items-center justify-center"
          >
            <CloudRain className="w-4 h-4 mr-1" />
            Models
          </ToggleGroupItem>
          <ToggleGroupItem
            value={BlockTypes.EXPORT}
            aria-label="Exports"
            className="flex-1 rounded-full px-3 py-1 text-sm flex items-center justify-center"
          >
            <Download className="w-4 h-4 mr-1" />
            Exports
          </ToggleGroupItem>
        </ToggleGroup>
      </div>
    </div>
  );
}
