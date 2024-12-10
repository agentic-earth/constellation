/**
 * Backend Connection Test Suite
 *
 * This test suite verifies the connection to our backend services and basic paper functionality.
 * It includes basic connectivity tests and simple paper retrieval operations.
 */

import { ping, getAllPapers } from "@/services/paperService";
import axios from "axios";

describe("Backend Connection Tests", () => {
  /**
   * Basic connectivity test
   */
  it("should connect to the backend successfully", async () => {
    console.log("Testing backend connection...");
    try {
      const response = await ping();
      console.log("Backend connection response:", response);
      expect(response).toEqual({ message: "pong" });
    } catch (error) {
      console.error("Backend connection failed:", error);
      throw error;
    }
  });

  /**
   * Test paper retrieval functionality
   */
  it("should retrieve test papers from backend", async () => {
    console.log("Testing paper retrieval...");
    try {
      const papers = await getAllPapers();
      console.log(`Retrieved ${papers.length} papers from backend`);

      // Verify paper structure
      if (papers.length > 0) {
        const firstPaper = papers[0];
        expect(firstPaper).toHaveProperty("id");
        expect(firstPaper).toHaveProperty("name");
        expect(firstPaper).toHaveProperty("block_type");

        // Log sample paper for debugging
        console.log("Sample paper structure:", {
          id: firstPaper.id,
          name: firstPaper.title,
          type: firstPaper.block_type,
        });
      }

      expect(Array.isArray(papers)).toBe(true);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Paper retrieval failed:", {
          status: error.response?.status,
          data: error.response?.data,
          message: error.message,
        });
      }
      throw error;
    }
  });

  /**
   * Test error handling
   */
  it("should handle backend errors gracefully", async () => {
    console.log("Testing error handling...");
    try {
      // Intentionally cause an error by requesting an invalid endpoint
      await axios.get("/invalid-endpoint");
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBeDefined();
        console.log("Error handled successfully:", {
          status: error.response?.status,
          message: error.message,
        });
      }
    }
  });
});
