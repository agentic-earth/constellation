"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TaskBubble } from "@/components/TaskBubble";
import {
  Search,
  CloudRain,
  Wind,
  Thermometer,
  Droplets,
  Sun,
  Waves,
  Snowflake,
} from "lucide-react";

interface SidebarProps {
  selectedModels: number[];
  onModelToggle: (modelId: number) => void;
  aoi: string;
  setAoi: (aoi: string) => void;
  apiEndpoint: string;
  runInference: () => void;
  weatherModels: Array<{ id: number; name: string; icon: React.ReactNode }>;
}

const weatherModels = [
  { id: 1, name: "GFS", icon: <CloudRain className="w-4 h-4" /> },
  { id: 2, name: "ECMWF", icon: <Wind className="w-4 h-4" /> },
  { id: 3, name: "UKMO", icon: <Thermometer className="w-4 h-4" /> },
  { id: 4, name: "CMC", icon: <Droplets className="w-4 h-4" /> },
  { id: 5, name: "ICON", icon: <Sun className="w-4 h-4" /> },
  { id: 6, name: "Météo-France", icon: <Waves className="w-4 h-4" /> },
  { id: 7, name: "JMA", icon: <Snowflake className="w-4 h-4" /> },
];

export const Sidebar: React.FC<SidebarProps> = ({
  selectedModels,
  onModelToggle,
  aoi,
  setAoi,
  apiEndpoint,
  runInference,
  weatherModels,
}) => {
  const [filter, setFilter] = useState("");

  const filteredModels = weatherModels.filter((model) =>
    model.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <Card className="w-full min-w-[300px] max-w-[400px] h-full bg-gray-50 rounded-lg overflow-hidden shadow-lg">
      <CardContent className="p-4 h-full flex flex-col">
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">
            Ensemble Weather Models
          </h2>
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="Search models"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="pl-10 rounded-full"
            />
          </div>
          <ScrollArea className="h-[300px] pr-4">
            <div className="grid grid-cols-1 gap-2">
              {filteredModels.map((model) => (
                <TaskBubble
                  key={model.id}
                  task={{ name: model.name, icon: model.icon }}
                  isSelected={selectedModels.includes(model.id)}
                  onClick={() => onModelToggle(model.id)}
                />
              ))}
            </div>
          </ScrollArea>
        </div>
        <div className="space-y-4 mb-6">
          <div>
            <Label htmlFor="aoi" className="text-sm font-medium">
              Area of Interest
            </Label>
            <Input
              id="aoi"
              value={aoi}
              onChange={(e) => setAoi(e.target.value)}
              placeholder="e.g., 'North America'"
              className="mt-1 rounded-full"
            />
          </div>
          <div>
            <Label htmlFor="api-endpoint" className="text-sm font-medium">
              Generated API Endpoint
            </Label>
            <Input
              id="api-endpoint"
              value={apiEndpoint}
              readOnly
              className="mt-1 rounded-full bg-gray-100"
            />
          </div>
        </div>
        <Button
          onClick={runInference}
          className="w-full rounded-full bg-blue-600 hover:bg-blue-700 text-white"
        >
          Run Ensemble Prediction
        </Button>
      </CardContent>
    </Card>
  );
};
