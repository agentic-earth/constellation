import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BotIcon, Send } from "lucide-react";

interface QueryInputProps {
  query: string;
  setQuery: (query: string) => void;
  handleSubmit: () => void;
  isLoading: boolean;
}

export function QueryInput({
  query,
  setQuery,
  handleSubmit,
  isLoading,
}: QueryInputProps) {
  return (
    <div className="w-full flex justify-center space-y-4">
      <div className="relative w-full max-w-md">
        <div className="flex items-center">
          <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
            <BotIcon className="w-6 h-6 text-muted-foreground" />
          </div>
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What do you want to create?"
            className="pl-12 pr-24 py-3 rounded-full bg-white/50 border-0 focus:ring-2 focus:ring-primary text-lg shadow-lg transition-all duration-300 ease-in-out flex-grow"
          />
          <Button
            onClick={handleSubmit}
            variant="default"
            size="lg"
            className="ml-2 rounded-full px-6 py-2 bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 ease-in-out"
            disabled={isLoading}
          >
            {isLoading ? "Processing..." : <Send className="w-5 h-5" />}
          </Button>
        </div>
      </div>
    </div>
  );
}
