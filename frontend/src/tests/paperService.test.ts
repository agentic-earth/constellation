/**
 * Paper Service API Tests
 *
 * This file contains tests for the Paper Service API. The tests are built up in complexity,
 * starting with a simple ping test to check the connection, followed by a test to retrieve
 * a single paper by its ID, and finally a test to perform a search query.
 *
 * How to run:
 * 1. Ensure you have Jest installed: `npm install jest ts-jest @types/jest --save-dev`
 * 2. Run the tests: `npx jest tests/paperService.test.ts`
 */

import {
  ping,
  getPaper,
  searchPapers,
  getInfo,
  getDatabaseStats,
  getAllPapers,
} from "@/services/paperService";
import { PaperType, SearchQuery, DatabaseStats } from "@/types/paperTypes";
import axios from "axios";

// Helper function to format date as YYYY-MM-DD
function formatDate(date: Date): string {
  return date.toISOString().split("T")[0];
}

// Mock data
const paperId = "2404.05746v1";
const searchQuery: SearchQuery = {
  keywords: ["climate", "model"],
  paper_type: PaperType.WEATHER_CLIMATE,
  date_range: [
    formatDate(new Date(new Date().setFullYear(new Date().getFullYear() - 10))),
    formatDate(new Date()),
  ],
  taxonomy_filters: {
    general: {
      spatial_scale: "Global",
    },
  },
  limit: 5,
  offset: 0,
};
describe("Paper Service API Tests", () => {
  /**
   * Test the ping endpoint to check if the API is running.
   */
  it("should ping the API successfully", async () => {
    console.log("Testing ping endpoint...");
    const response = await ping();
    console.log("Ping response:", response);
    expect(response).toEqual({ message: "pong" });
  });

  /**
   * Test retrieving a single paper by its ID.
   */
  it("should retrieve a paper by ID", async () => {
    console.log(`Testing getPaper endpoint with paper ID: ${paperId}...`);
    const response = await getPaper(paperId);
    console.log("Get paper response:", response);
    expect(response).toHaveProperty("id", paperId);
  });

  /**
   * Test performing a search query.
   */
  it("should perform a search query", async () => {
    console.log("Testing searchPapers endpoint with query:", searchQuery);
    try {
      const response = await searchPapers(searchQuery);
      console.log("Search response:", response);
      expect(response).toHaveProperty("papers");
      expect(response.papers.length).toBeGreaterThan(0);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Axios error response data:", error.response?.data);
      }
      throw error;
    }
  });

  /**
   * Test the info endpoint to check if the API info is retrieved.
   */
  it("should retrieve API info", async () => {
    console.log("Testing info endpoint...");
    const response = await getInfo();
    console.log("Info response:", response);
    expect(response).toHaveProperty("app_name");
    expect(response).toHaveProperty("version");
    expect(response).toHaveProperty("endpoints");
  });

  /**
   * Test retrieving all papers from the database.
   */
  it("should retrieve all papers", async () => {
    console.log("Testing getAllPapers endpoint...");
    try {
      const response = await getAllPapers();
      console.log(`Retrieved ${response.length} papers`);
      expect(Array.isArray(response)).toBe(true);
      expect(response.length).toBeGreaterThan(0);
      expect(response[0]).toHaveProperty("id");
      expect(response[0]).toHaveProperty("title");
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Axios error response data:", error.response?.data);
      }
      throw error;
    }
  });

  /**
   * Test retrieving database statistics.
   */
  it("should retrieve database statistics", async () => {
    console.log("Testing getDatabaseStats endpoint...");
    try {
      const response: DatabaseStats = await getDatabaseStats();
      console.log("Database stats:", response);
      expect(response).toHaveProperty("total_papers");
      expect(typeof response.total_papers).toBe("number");
      expect(response).toHaveProperty("papers_by_type");
      expect(typeof response.papers_by_type).toBe("object");
      expect(Object.keys(response.papers_by_type).length).toBeGreaterThan(0);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Axios error response data:", error.response?.data);
      }
      throw error;
    }
  });
});
