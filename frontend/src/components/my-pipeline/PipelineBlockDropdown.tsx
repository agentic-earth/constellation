import React, { useState, KeyboardEvent } from "react";
import { Key, Check } from "lucide-react";
import { BlockType, BlockTypes } from "@/types/blockTypes";

interface PipelineBlockDropdownProps {
  type: BlockType;
  onApiKeyChange?: (key: string) => void;
}

export function PipelineBlockDropdown({
  type,
  onApiKeyChange,
}: PipelineBlockDropdownProps) {
  const [apiKey, setApiKey] = useState("");
  const [isKeyConfirmed, setIsKeyConfirmed] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setApiKey(e.target.value);
    setIsKeyConfirmed(false);
    if (onApiKeyChange) {
      onApiKeyChange(e.target.value);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setIsKeyConfirmed(true);
    }
  };

  return (
    <div className="w-full">
      {type === BlockTypes.MODEL && (
        <div className="flex items-center bg-black rounded p-2">
          {isKeyConfirmed ? (
            <Check className="text-green-500 mr-2" size={16} />
          ) : (
            <Key className="text-white mr-2" size={16} />
          )}
          <input
            type="text"
            value={apiKey}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            className="flex-grow bg-black text-white placeholder-gray-400 focus:outline-none text-sm"
            placeholder="Enter API Key"
          />
        </div>
      )}
      {/* Add more conditional fields based on block type */}
    </div>
  );
}
