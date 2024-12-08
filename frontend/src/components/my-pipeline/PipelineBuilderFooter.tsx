import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Download } from "lucide-react";

interface PipelineBuilderFooterProps {
  hasBlocks: boolean;
}

export function PipelineBuilderFooter({
  hasBlocks,
}: PipelineBuilderFooterProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleDownload = async () => {
    setIsDownloading(true);
    setProgress(0);

    // Simulate download progress
    for (let i = 0; i <= 100; i += 10) {
      setProgress(i);
      await new Promise((resolve) => setTimeout(resolve, 500));
    }

    // Download cat picture
    const response = await fetch("https://cataas.com/cat");
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = "cat.jpg";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);

    setIsDownloading(false);
  };

  if (!hasBlocks) return null;

  return (
    <section className="w-full py-6 bg-gradient-to-br from-primary to-primary/90 mt-8">
      <div className="container mx-auto px-4 md:px-6">
        <Card className="w-full max-w-4xl mx-auto bg-primary-foreground/10 rounded-3xl overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-primary-foreground/20 group">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-black">Pipeline Ready</h3>
              <Button
                onClick={handleDownload}
                disabled={isDownloading}
                size="lg"
                className="bg-secondary text-secondary-foreground hover:bg-secondary/90 rounded-full transition-all duration-300 hover:scale-105"
              >
                {isDownloading
                  ? "Downloading..."
                  : "Download Pipeline as Docker Image"}
                <Download className="ml-2 h-4 w-4" />
              </Button>
            </div>
            {isDownloading && (
              <Progress
                value={progress}
                className="mt-4 bg-primary-foreground/20"
              />
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
