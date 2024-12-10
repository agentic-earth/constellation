// PipelineWorkspace.tsx
import React, {
  useRef,
  useState,
  useEffect,
  useCallback,
  useContext,
} from "react";
import { useDrop } from "react-dnd";
import { PipelineBlock } from "./PipelineBlock";
import { PipelineConnection } from "./PipelineConnection";
import { PipelineWorkspaceControls } from "./PipelineWorkspaceControls";
import { BlockTypes } from "@/types/blockTypes";
import { useToast } from "@/hooks/use-toast";
import { Block } from "@/types/pipelineTypes";
import { PipelineContext } from "@/contexts/PipelineContext";
import { v4 as uuidv4 } from "uuid"; // Ensure you have uuid installed for unique IDs
import {
  createGeneratedPipeline,
  runPipeline,
} from "@/services/pipelineService";

interface Connection {
  id: string;
  source: string;
  target: string;
}

interface PipelineWorkspaceProps {
  onClearAll: () => void;
}

export function PipelineWorkspace({ onClearAll }: PipelineWorkspaceProps) {
  const {
    blocks,
    setBlocks,
    connections,
    setConnections,
    dagsterConfig,
    setDagsterConfig,
  } = useContext(PipelineContext)!;
  const workspaceRef = useRef<HTMLDivElement>(null);
  const [scrollPosition, setScrollPosition] = useState({ x: 0, y: 0 });
  const [selectedBlockId, setSelectedBlockId] = useState<string | null>(null);
  const { toast } = useToast();

  const [blockDimensions, setBlockDimensions] = useState<{
    [key: string]: { width: number; height: number };
  }>({});

  const [isDraggingBlock, setIsDraggingBlock] = useState(false);
  const [draggingBlockId, setDraggingBlockId] = useState<string | null>(null);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({
    x: 0,
    y: 0,
  });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState<{ x: number; y: number }>({
    x: 0,
    y: 0,
  });
  const [scrollStart, setScrollStart] = useState<{ x: number; y: number }>({
    x: 0,
    y: 0,
  });
  const [zoomLevel, setZoomLevel] = useState(1);

  const [isDeploying, setIsDeploying] = useState(false);

  const deployPipeline = async () => {
    setIsDeploying(true);

    // Add an info toast to notify the user that deployment is starting
    toast({
      title: "Deployment Started",
      description: "Your pipeline is being deployed.",
      variant: "default",
    });

    // List out the blocks in the order they are connected
    const blockOrder: string[] = [];
    const visited = new Set<string>();
    const dfs = (blockId: string) => {
      if (visited.has(blockId)) return;
      visited.add(blockId);
      blockOrder.push(blockId);
    };

    for (const block of blocks) {
      dfs(block.id);
    }

    const orderedBlockNames = blockOrder.map((blockId) => {
      const block = blocks.find((b) => b.id === blockId);
      return block?.name;
    });
    const prefixText =
      "I have the following blocks in order and would like to create a pipeline with them:";
    const query = prefixText + orderedBlockNames.join(",");
    const data = await createGeneratedPipeline(query);
    setDagsterConfig(data.pipeline.ops.generate_dynamic_job_configs.config);
    const deployData = await runPipeline(dagsterConfig);

    if (deployData) {
      toast({
        title: "Deployment Successful",
        description: "Your pipeline has been deployed.",
        variant: "default",
      });
    }

    setIsDeploying(false);
  };

  // Handle dropping new blocks into the workspace
  const handleDrop = useCallback(
    (item: Block, monitor) => {
      const offset = monitor.getClientOffset();
      if (offset && workspaceRef.current) {
        const workspaceRect = workspaceRef.current.getBoundingClientRect();
        const x =
          (offset.x - workspaceRect.left + workspaceRef.current.scrollLeft) /
          zoomLevel;
        const y =
          (offset.y - workspaceRect.top + workspaceRef.current.scrollTop) /
          zoomLevel;
        const newBlock = {
          ...item,
          id: `${item.type}-${Date.now()}`,
          position: { x, y },
        };
        setBlocks((prevBlocks) => [...prevBlocks, newBlock]);
        console.log("New block added:", newBlock);
      }
    },
    [setBlocks, zoomLevel],
  );

  const [, drop] = useDrop(
    () => ({
      accept: [BlockTypes.MODEL, BlockTypes.DATASET, BlockTypes.EXPORT],
      drop: handleDrop,
    }),
    [handleDrop],
  );

  // Handle dragging blocks
  const handleBlockMouseDown = (e: React.MouseEvent, blockId: string) => {
    e.stopPropagation();
    setIsDraggingBlock(true);
    setDraggingBlockId(blockId);
    setDragStart({ x: e.pageX, y: e.pageY });
    console.log(`Started dragging block ${blockId}`);
  };

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (isDraggingBlock && draggingBlockId && workspaceRef.current) {
        e.preventDefault();

        const workspaceRect = workspaceRef.current.getBoundingClientRect();

        const deltaX = (e.pageX - dragStart.x) / zoomLevel;
        const deltaY = (e.pageY - dragStart.y) / zoomLevel;

        setBlocks((prevBlocks) =>
          prevBlocks.map((block) =>
            block.id === draggingBlockId
              ? {
                  ...block,
                  position: {
                    x: block.position.x + deltaX,
                    y: block.position.y + deltaY,
                  },
                }
              : block,
          ),
        );
        setDragStart({ x: e.pageX, y: e.pageY });

        console.log(`Dragging block ${draggingBlockId} to new position`);
      } else if (isPanning && workspaceRef.current) {
        e.preventDefault();
        const deltaX = e.clientX - panStart.x;
        const deltaY = e.clientY - panStart.y;
        workspaceRef.current.scrollLeft = scrollStart.x - deltaX;
        workspaceRef.current.scrollTop = scrollStart.y - deltaY;
      }
    },
    [
      isDraggingBlock,
      draggingBlockId,
      dragStart,
      setBlocks,
      zoomLevel,
      isPanning,
      panStart,
      scrollStart,
    ],
  );

  const handleMouseUp = useCallback(() => {
    if (isDraggingBlock) {
      setIsDraggingBlock(false);
      setDraggingBlockId(null);
      console.log(`Stopped dragging block`);
    }
    if (isPanning) {
      setIsPanning(false);
    }
  }, [isDraggingBlock, isPanning]);

  useEffect(() => {
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  // Handle mouse down on the workspace for panning
  const handleWorkspaceMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return; // Only respond to left-click
    setIsPanning(true);
    setPanStart({ x: e.clientX, y: e.clientY });
    if (workspaceRef.current) {
      setScrollStart({
        x: workspaceRef.current.scrollLeft,
        y: workspaceRef.current.scrollTop,
      });
    }
    setSelectedBlockId(null); // Deselect the current block
  };

  // Zoom handling
  const handleWheel = (e: React.WheelEvent) => {
    if (e.ctrlKey) {
      e.preventDefault();
      const delta = -e.deltaY / 500;
      setZoomLevel((prevZoom) => Math.min(Math.max(prevZoom + delta, 0.5), 3));
    }
  };

  // Handle block click for selection and connection
  const handleBlockClick = async (e: React.MouseEvent, blockId: string) => {
    e.stopPropagation();
    if (selectedBlockId === null) {
      setSelectedBlockId(blockId);
    } else if (selectedBlockId === blockId) {
      setSelectedBlockId(null);
    } else {
      // Handle block connection logic
      const existingConnection = connections.find(
        (conn) =>
          (conn.source === selectedBlockId && conn.target === blockId) ||
          (conn.source === blockId && conn.target === selectedBlockId),
      );
      if (!existingConnection) {
        // setConnections((prevConnections) => [
        //   ...prevConnections,
        //   { source: selectedBlockId, target: blockId },
        // ]);
        // setSelectedBlockId(null);
        const id = uuidv4();
        const newConnection = {
          id: id,
          source: selectedBlockId, // Dynamic block ID from state
          target: blockId, // Dynamic block ID from state
        };

        // Add the connection to the local state
        setConnections((prevConnections) => [
          ...prevConnections,
          newConnection,
        ]);

        // Post the new connection to the backend
        try {
          // const response = await fetch(
          //   "http://127.0.0.1:8081/edges/?user_id=${id}",
          //   {
          //     method: "POST",
          //     headers: {
          //       "Content-Type": "application/json",
          //     },
          //     body: JSON.stringify({
          //       source_block_id: selectedBlockId, // Dynamic block ID
          //       target_block_id: blockId, // Dynamic block ID
          //     }),
          //   }
          // );

          // if (!response.ok) {
          //   throw new Error("Failed to create edge on the server.");
          // }

          console.log("Edge created successfully on the server.");
        } catch (error) {
          console.error("Error creating edge:", error);
          toast({
            title: "Connection Error",
            description: "Failed to create the connection on the server.",
            variant: "destructive",
          });
        }
      } else {
        // toast({
        //   title: "Invalid Connection",
        //   description: "These blocks are already connected.",
        //   variant: "destructive",
        // });
      }
    }
  };

  // Handle delete block
  const handleDeleteBlock = (blockId: string) => {
    setBlocks((prevBlocks) =>
      prevBlocks.filter((block) => block.id !== blockId),
    );
    setConnections((prevConnections) =>
      prevConnections.filter(
        (conn) => conn.source !== blockId && conn.target !== blockId,
      ),
    );
    if (selectedBlockId === blockId) {
      setSelectedBlockId(null);
    }
  };

  // Handle recentering the workspace
  const handleRecenter = () => {
    if (workspaceRef.current) {
      workspaceRef.current.scrollTo({
        top:
          workspaceRef.current.scrollHeight / 2 -
          workspaceRef.current.clientHeight / 2,
        left:
          workspaceRef.current.scrollWidth / 2 -
          workspaceRef.current.clientWidth / 2,
        behavior: "smooth",
      });
    }
  };

  // Handle zoom controls
  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.1, 3));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.1, 0.5));
  const handleResetZoom = () => setZoomLevel(1);

  // Update scroll position
  useEffect(() => {
    const workspace = workspaceRef.current;
    if (!workspace) return;

    const handleScroll = () => {
      setScrollPosition({
        x: workspace.scrollLeft,
        y: workspace.scrollTop,
      });
    };

    workspace.addEventListener("scroll", handleScroll);

    return () => {
      workspace.removeEventListener("scroll", handleScroll);
    };
  }, []);

  const handleBlockDimensionsChange = useCallback(
    (id: string, width: number, height: number) => {
      setBlockDimensions((prev) => ({
        ...prev,
        [id]: { width, height },
      }));
    },
    [],
  );

  // Add a delete connection handler
  const handleDeleteConnection = (connectionId: string) => {
    setConnections((prevConnections) =>
      prevConnections.filter((conn) => conn.id !== connectionId),
    );
  };

  return (
    <div
      ref={drop as unknown as React.LegacyRef<HTMLDivElement>}
      className="relative w-full h-[calc(100vh-12rem)] overflow-hidden"
      onWheel={handleWheel}
    >
      <div className="absolute top-4 right-4 z-10">
        <PipelineWorkspaceControls
          onRecenter={handleRecenter}
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onReset={handleResetZoom}
          zoomLevel={zoomLevel}
          onClearAll={onClearAll}
          onSave={() => {}}
          onLoad={() => {}}
          onDownload={() => {}}
        />
      </div>
      <div
        ref={workspaceRef}
        className="relative w-full h-full bg-white rounded-2xl shadow-inner overflow-scroll custom-scrollbar"
        style={{
          cursor: isPanning ? "grabbing" : "default",
          backgroundImage:
            "radial-gradient(circle, #d1d1d1 1px, transparent 1px)",
          backgroundSize: `${40 * zoomLevel}px ${40 * zoomLevel}px`,
          backgroundPosition: `${
            (-scrollPosition.x * zoomLevel) % (40 * zoomLevel)
          }px ${(-scrollPosition.y * zoomLevel) % (40 * zoomLevel)}px`,
        }}
        onMouseDown={handleWorkspaceMouseDown}
      >
        <div
          className="absolute inset-0"
          style={{
            transform: `scale(${zoomLevel})`,
            transformOrigin: "top left",
          }}
        >
          {blocks.map((block) => (
            <PipelineBlock
              key={block.id}
              id={block.id}
              name={block.name}
              type={block.type}
              dataSources={block.dataSources}
              position={block.position}
              isSelected={selectedBlockId === block.id}
              onMouseDown={(e) => handleBlockMouseDown(e, block.id)}
              onClick={(e) => handleBlockClick(e, block.id)}
              onDelete={() => handleDeleteBlock(block.id)}
              onDimensionsChange={handleBlockDimensionsChange}
            />
          ))}

          {connections.map((connection) => {
            const sourceBlock = blocks.find((b) => b.id === connection.source);
            const targetBlock = blocks.find((b) => b.id === connection.target);
            if (sourceBlock && targetBlock) {
              return (
                <PipelineConnection
                  key={connection.id}
                  id={connection.id}
                  sourceBlock={sourceBlock}
                  targetBlock={targetBlock}
                  sourceDimensions={blockDimensions[sourceBlock.id]}
                  targetDimensions={blockDimensions[targetBlock.id]}
                  onDelete={() => handleDeleteConnection(connection.id)}
                />
              );
            }
            return null;
          })}
        </div>
      </div>
      <button
        className={`absolute bottom-4 right-4 py-2 px-4 rounded shadow-lg ${
          blocks.length === 0 || isDeploying
            ? "bg-gray-400 text-gray-700 cursor-not-allowed"
            : "bg-blue-500 text-white hover:bg-blue-600"
        }`}
        disabled={blocks.length === 0 || isDeploying}
        onClick={deployPipeline}
      >
        Deploy
      </button>
    </div>
  );
}
