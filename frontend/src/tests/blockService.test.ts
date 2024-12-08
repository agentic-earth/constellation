import { BlockService } from '@/services/routeServices';
import { handleBlockDrop } from '@/utils/pipelineWorkspaceUtils';
import { canConnect } from '@/utils/pipelineUtils';
import { BlockTypes} from '@/types/blockTypes';
import { SatelliteSource } from "@/types/paperTypes";
import { v4 as uuidv4 } from 'uuid';

global.DOMRect = class DOMRect {
  constructor(x: number, y: number, width: number, height: number) {
    return { x, y, width, height };
  }
} as any;

describe('Block Controller Tests', () => {
  const blockService = new BlockService();
  const userId = uuidv4();

  const mockWorkspaceRect = new DOMRect(0, 0, 1000, 1000);
  const mockScrollPosition = { x: 0, y: 0 };
  const mockZoomLevel = 1;

  it('should create a block with correct position', async () => {
    const blockData = {
      id: "some-unique-id",
      name: "Sentinel-2 Dataset",
      type: BlockTypes.DATASET,
      dataSources: [SatelliteSource.SENTINEL_2],
      position: { x: 0, y: 0 }
    };

    const droppedBlock = handleBlockDrop(
      blockData,
      { x: 100, y: 100 },
      mockWorkspaceRect,
      mockScrollPosition,
      mockZoomLevel
    );

    const response = await blockService.createBlock({
      name: droppedBlock.name,
      block_type: droppedBlock.type,
      description: `Dataset for ${droppedBlock.name}`
    }, userId);

    expect(response).toHaveProperty('block_id');
    expect(response.name).toBe(blockData.name);
  });

  it('should validate block connections', async () => {
    const sourceBlock = {
      id: '1',
      name: "Sentinel-2 Dataset",
      type: BlockTypes.DATASET,
      dataSources: [SatelliteSource.SENTINEL_2],
      position: { x: 0, y: 0 }
    };

    const targetBlock = {
      id: '2',
      name: "MODIS Fire Detection",
      type: BlockTypes.MODEL,
      dataSources: [SatelliteSource.SENTINEL_2],
      position: { x: 200, y: 0 }
    };

    const canConnectBlocks = canConnect(sourceBlock, targetBlock);
    expect(canConnectBlocks).toBe(true);
  });
});
