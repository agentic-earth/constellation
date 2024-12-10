import React from "react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Satellite, CloudRain, Database } from "lucide-react";

interface SidebarTabsProps {
  activeTab: string;
  onTabChange: (value: string) => void;
}

export function SidebarTabs({ activeTab, onTabChange }: SidebarTabsProps) {
  return (
    <Tabs value={activeTab} onValueChange={onTabChange} className="w-full">
      <TabsList className="w-full rounded-t-lg bg-gray-100 p-0.5 flex">
        <TabsTrigger
          value="earth-observation"
          className="flex-1 text-[8px] xs:text-[10px] sm:text-xs lg:text-sm py-1 px-0.5 sm:px-1"
        >
          <Satellite className="w-3 h-3 sm:w-4 sm:h-4 mr-0.5 flex-shrink-0" />
          <span className="truncate hidden xs:inline">Earth Observation</span>
          <span className="truncate xs:hidden">EO</span>
        </TabsTrigger>
        <TabsTrigger
          value="climate-weather"
          className="flex-1 text-[8px] xs:text-[10px] sm:text-xs lg:text-sm py-1 px-0.5 sm:px-1"
        >
          <CloudRain className="w-3 h-3 sm:w-4 sm:h-4 mr-0.5 flex-shrink-0" />
          <span className="truncate hidden xs:inline">Climate Prediction</span>
          <span className="truncate xs:hidden">Climate</span>
        </TabsTrigger>
        <TabsTrigger
          value="datasets"
          className="flex-1 text-[8px] xs:text-[10px] sm:text-xs lg:text-sm py-1 px-0.5 sm:px-1"
        >
          <Database className="w-3 h-3 sm:w-4 sm:h-4 mr-0.5 flex-shrink-0" />
          <span className="truncate">Datasets</span>
        </TabsTrigger>
      </TabsList>
    </Tabs>
  );
}
