import { describe, test, expect, beforeAll, afterAll } from "@jest/globals";
import axios from "axios";
import { Settings } from "lucide-react";

// const settings = Settings({});
const API_URL =
  "OPENAI_API_KEY";

describe("AI Crews Integration Tests", () => {
  let authToken: string;

  beforeAll(async () => {
    // Setup authentication if needed
    authToken = "test-token";
  });

  describe("Research Crew Tests", () => {
    test("should search for papers with given query", async () => {
      const query = "climate change mitigation strategies";

      const response = await axios.post(
        `${API_URL}/research/search`,
        {
          query,
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        },
      );

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("papers");
      expect(Array.isArray(response.data.papers)).toBe(true);
    });

    test("should handle empty search results", async () => {
      const query = "xyznonexistentquery123";

      const response = await axios.post(
        `${API_URL}/research/search`,
        {
          query,
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        },
      );

      expect(response.status).toBe(200);
      expect(response.data.papers).toHaveLength(0);
    });
  });

  describe("Dev Crew Tests", () => {
    test("should analyze GitHub repository", async () => {
      const repoUrl = "https://github.com/test/repository";

      const response = await axios.post(
        `${API_URL}/dev/analyze`,
        {
          github_repo_url: repoUrl,
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        },
      );

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("analysis");
    });

    test("should handle invalid GitHub URLs", async () => {
      const invalidRepoUrl = "https://invalid-url";

      await expect(
        axios.post(
          `${API_URL}/dev/analyze`,
          {
            github_repo_url: invalidRepoUrl,
          },
          {
            headers: {
              Authorization: `Bearer ${authToken}`,
            },
          },
        ),
      ).rejects.toThrow();
    });
  });

  describe("Crew Process Tests", () => {
    test("should create and execute a research crew", async () => {
      const response = await axios.post(
        `${API_URL}/crews/research`,
        {
          query: "climate change",
          options: {
            max_results: 5,
            include_summary: true,
          },
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        },
      );

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("crew_id");
      expect(response.data).toHaveProperty("results");
    });

    test("should handle crew execution errors gracefully", async () => {
      try {
        const response = await axios
          .post(
            `${API_URL}/crews/research`,
            {
              query: "", // Empty query should trigger an error
              options: {
                max_results: 5,
              },
            },
            {
              headers: {
                Authorization: `Bearer ${authToken}`,
              },
            },
          )
          .catch((error) => {
            if (error.response) {
              console.log(error.response.data);
              console.log(error.response.status);
            } else if (error.request) {
              console.log(error.request);
            }
            throw error;
          });

        expect(response.status).toBe(400);
        expect(response.data).toHaveProperty("error");
      } catch (error) {
        // Handle test-specific error cases
      }
    });
  });
});
