import React from "react";
import { useDrag } from "react-dnd";
import { Card, CardContent, Badge } from "@/components/ui";
import { Satellite, CloudRain, Download } from "lucide-react";
import { BlockTypes, BlockType } from "@/types/blockTypes";
import { FullPaper } from "@/types/paperTypes";

interface Block {
  id?: string;
  name: string;
  type: BlockType;
  dataSources: string[];
  paperData?: FullPaper;
}

export const DraggableBlock = ({ block }: { block: Block }) => {
  const [{ isDragging }, drag] = useDrag(
    () => ({
      type: block.type || "defaultType",
      item: { ...block },
      collect: (monitor) => ({
        isDragging: !!monitor.isDragging(),
      }),
    }),
    [block]
  );

  return (
    <div
      ref={drag as unknown as React.LegacyRef<HTMLDivElement>}
      style={{ opacity: isDragging ? 0.5 : 1 }}
    >
      <Card
        className={`mb-2 cursor-move bg-white rounded-3xl shadow-sm hover:shadow-md transition-shadow duration-200`}
      >
        <CardContent className="p-3">
          <div className="flex items-center">
            {block.type === BlockTypes.DATASET ? (
              <Satellite className="w-5 h-5 mr-2 text-green-500" />
            ) : block.type === BlockTypes.EXPORT ? (
              <Download className="w-5 h-5 mr-2 text-red-500" />
            ) : (
              <CloudRain className="w-5 h-5 mr-2 text-blue-500" />
            )}
            <p className="text-sm font-medium flex-1 line-clamp-1">
              {block.name}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
