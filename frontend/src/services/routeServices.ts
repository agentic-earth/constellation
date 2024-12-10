import apiClient from "@/lib/apiClient";
import { Block } from "@/types/blockTypes";
import { Connection } from "@/types/pipelineTypes";
import { UUID } from "crypto";

// Request Types
interface CreateBlockRequest {
  name: string;
  block_type: string;
  description?: string;
  text?: string;
}

interface CreateEdgeRequest {
  source_block_id: UUID;
  target_block_id: UUID;
  edge_type: string;
}

interface CreatePipelineRequest {
  name: string;
  description?: string;
  blocks: UUID[];
  edges: CreateEdgeRequest[];
}

// Service Classes
export class BlockService {
  async createBlock(
    blockData: CreateBlockRequest,
    userId: UUID,
  ): Promise<Block> {
    try {
      const response = await apiClient.post<Block>("/blocks", blockData, {
        headers: { "user-id": userId },
      });
      return response.data;
    } catch (error) {
      console.error("Error creating block:", error);
      throw error;
    }
  }

  async searchBlocksByVector(
    query: string,
    userId: UUID,
    topK: number = 10,
  ): Promise<Block[]> {
    try {
      const response = await apiClient.post<Block[]>(
        "/blocks/search-by-vector",
        {
          query,
          top_k: topK,
        },
        {
          headers: { "user-id": userId },
        },
      );
      return response.data;
    } catch (error) {
      console.error("Error searching blocks by vector:", error);
      throw error;
    }
  }

  async getBlockVector(blockId: UUID, userId: UUID): Promise<number[]> {
    try {
      const response = await apiClient.get<number[]>(
        `/blocks/${blockId}/vector`,
        {
          headers: { "user-id": userId },
        },
      );
      return response.data;
    } catch (error) {
      console.error("Error getting block vector:", error);
      throw error;
    }
  }
}

export class EdgeService {
  async createEdge(
    edgeData: CreateEdgeRequest,
    userId: UUID,
  ): Promise<Connection> {
    try {
      const response = await apiClient.post<Connection>("/edges", edgeData, {
        headers: { "user-id": userId },
      });
      return response.data;
    } catch (error) {
      console.error("Error creating edge:", error);
      throw error;
    }
  }

  async getEdge(edgeId: UUID, userId: UUID): Promise<Connection> {
    try {
      const response = await apiClient.get<Connection>(`/edges/${edgeId}`, {
        headers: { "user-id": userId },
      });
      return response.data;
    } catch (error) {
      console.error("Error getting edge:", error);
      throw error;
    }
  }
}

export class PipelineService {
  async createPipeline(pipelineData: CreatePipelineRequest, userId: UUID) {
    try {
      const response = await apiClient.post("/pipelines", pipelineData, {
        headers: { "user-id": userId },
      });
      return response.data;
    } catch (error) {
      console.error("Error creating pipeline:", error);
      throw error;
    }
  }

  async verifyPipeline(pipelineId: UUID, userId: UUID): Promise<boolean> {
    try {
      const response = await apiClient.post(
        `/pipelines/verify/${pipelineId}`,
        {},
        { headers: { "user-id": userId } },
      );
      return response.data.verified;
    } catch (error) {
      console.error("Error verifying pipeline:", error);
      throw error;
    }
  }
}

export class UserService {
  async registerUser(userData: {
    email: string;
    password: string;
    username: string;
  }) {
    try {
      const response = await apiClient.post("/users/register", userData);
      return response.data;
    } catch (error) {
      console.error("Error registering user:", error);
      throw error;
    }
  }

  async createApiKey(userId: UUID) {
    try {
      const response = await apiClient.post(`/users/${userId}/api-keys`);
      return response.data;
    } catch (error) {
      console.error("Error creating API key:", error);
      throw error;
    }
  }

  async revokeApiKey(userId: UUID, apiKeyId: UUID): Promise<boolean> {
    try {
      const response = await apiClient.delete(
        `/users/${userId}/api-keys/${apiKeyId}`,
      );
      return response.data.success;
    } catch (error) {
      console.error("Error revoking API key:", error);
      throw error;
    }
  }
}
