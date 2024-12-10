/**
 * Paper Search API Service
 *
 * This service provides methods to interact with the Paper Search API, which includes
 * endpoints for searching and retrieving scientific papers related to Earth observation,
 * climate, and weather models. The API allows users to search for papers based on various
 * criteria and retrieve detailed information about specific papers.
 *
 * Main Endpoints:
 * 1. POST /search
 *    - Input: SearchQuery object in the request body
 *    - Output: SearchResult object
 *
 * 2. GET /paper/{paper_id}
 *    - Input: paper_id as a path parameter
 *    - Output: FullPaper object
 *
 * 3. GET /recent_papers
 *    - Input: limit as a query parameter (optional, default=10)
 *    - Output: List of FullPaper objects
 *
 * 4. GET /ping
 *    - Output: {"message": "pong"}
 *
 * 5. GET /info
 *    - Output: Information about the API, including available endpoints
 *
 * Error Handling:
 * - 404: Paper not found
 * - 422: Validation error (e.g., invalid input format)
 * - 500: Unexpected server error
 */
import apiClient from "@/lib/apiClient";
import {
  SearchQuery,
  SearchResult,
  FullPaper,
  DatabaseStats,
  PaperType,
} from "@/types/paperTypes";

/**
 * Search for papers based on the provided search query.
 * @param {SearchQuery} searchQuery - The search query object.
 * @returns {Promise<SearchResult>} - The search result object.
 */
export const searchPapers = async (
  searchQuery: SearchQuery,
): Promise<SearchResult> => {
  try {
    console.log("Sending search request with query:", searchQuery);
    const response = await apiClient.post<SearchResult>("/search", searchQuery);
    console.log("Received search response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error searching papers:", error);
    throw error;
  }
};

/**
 * Clean the search query by removing empty filters.
 * @param {SearchQuery} query - The original search query.
 * @returns {SearchQuery} - The cleaned search query.
 */
function cleanSearchQuery(query: SearchQuery): SearchQuery {
  const cleanedQuery = { ...query };

  // If there's a search term, add it to the keywords
  if (cleanedQuery.searchTerm) {
    cleanedQuery.keywords = cleanedQuery.keywords || [];
    cleanedQuery.keywords.push(cleanedQuery.searchTerm);
    delete cleanedQuery.searchTerm;
  }

  if (cleanedQuery.taxonomy_filters) {
    for (const key in cleanedQuery.taxonomy_filters) {
      if (cleanedQuery.taxonomy_filters.hasOwnProperty(key)) {
        const filter =
          cleanedQuery.taxonomy_filters[
            key as keyof typeof cleanedQuery.taxonomy_filters
          ];
        if (filter && typeof filter === "object") {
          // Remove empty arrays or objects
          for (const subKey in filter) {
            if (filter.hasOwnProperty(subKey)) {
              const value = filter[subKey as keyof typeof filter];
              if (Array.isArray(value) && value.length === 0) {
                delete filter[subKey as keyof typeof filter];
              } else if (
                typeof value === "object" &&
                value !== null &&
                Object.keys(value).length === 0
              ) {
                delete filter[subKey as keyof typeof filter];
              }
            }
          }
          // If the filter is now empty, remove it
          if (Object.keys(filter).length === 0) {
            delete cleanedQuery.taxonomy_filters[
              key as keyof typeof cleanedQuery.taxonomy_filters
            ];
          }
        } else {
          delete cleanedQuery.taxonomy_filters[
            key as keyof typeof cleanedQuery.taxonomy_filters
          ];
        }
      }
    }

    // If all taxonomy filters are empty, remove the entire taxonomy_filters object
    if (Object.keys(cleanedQuery.taxonomy_filters).length === 0) {
      delete cleanedQuery.taxonomy_filters;
    }
  }

  // Remove empty keywords array
  if (
    Array.isArray(cleanedQuery.keywords) &&
    cleanedQuery.keywords.length === 0
  ) {
    delete cleanedQuery.keywords;
  }

  // Handle date_range
  if (cleanedQuery.date_range && cleanedQuery.date_range.length > 0) {
    const [startDate] = cleanedQuery.date_range;
    if (startDate) {
      cleanedQuery.date_range = [startDate, new Date().toISOString()];
    } else {
      delete cleanedQuery.date_range;
    }
  } else {
    delete cleanedQuery.date_range;
  }

  return cleanedQuery;
}

/**
 * Retrieve detailed information about a specific paper.
 * @param {string} paperId - The ID of the paper to retrieve.
 * @returns {Promise<FullPaper>} - The full paper object.
 */
export const getPaper = async (paperId: string): Promise<FullPaper> => {
  try {
    console.log(`Sending request to get paper with ID: ${paperId}`);
    const response = await apiClient.get<FullPaper>(`/paper/${paperId}`);
    console.log("Received paper response:", response.data);
    return response.data;
  } catch (error) {
    console.error(`Error retrieving paper with ID ${paperId}:`, error);
    throw error;
  }
};

/**
 * Retrieve a list of recent papers.
 * @param {number} [limit=10] - The maximum number of recent papers to retrieve.
 * @returns {Promise<FullPaper[]>} - The list of recent papers.
 */
export const getRecentPapers = async (limit = 10): Promise<FullPaper[]> => {
  try {
    console.log(`Sending request to get recent papers with limit: ${limit}`);
    const response = await apiClient.get<FullPaper[]>("/recent_papers", {
      params: { limit },
    });
    console.log("Received recent papers response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error retrieving recent papers:", error);
    throw error;
  }
};

/**
 * Ping the API to check if it's running.
 * @returns {Promise<{ message: string }>} - The ping response.
 */
export const ping = async (): Promise<{ message: string }> => {
  try {
    console.log("Sending ping request");
    const response = await apiClient.get<{ message: string }>("/ping");
    console.log("Received ping response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error pinging API:", error);
    throw error;
  }
};

/**
 * Get information about the API, including available endpoints.
 * @returns {Promise<Object>} - The API info.
 */
export const getInfo = async (): Promise<Object> => {
  try {
    console.log("Sending request to get API info");
    const response = await apiClient.get<Object>("/info");
    console.log("Received API info response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error retrieving API info:", error);
    throw error;
  }
};

/**
 * Retrieve all papers from the database.
 * @returns {Promise<FullPaper[]>} - An array of all papers in the database.
 */
export const getAllPapers = async (): Promise<FullPaper[]> => {
  try {
    console.log("Sending request to get all papers");
    const response = await apiClient.get<FullPaper[]>("/all_papers");
    console.log(`Received ${response.data.length} papers from the database`);
    return response.data;
  } catch (error) {
    console.error("Error retrieving all papers:", error);
    throw error;
  }
};

/**
 * Retrieve database statistics.
 * @returns {Promise<DatabaseStats>} - Statistics about the papers in the database.
 */
export const getDatabaseStats = async (): Promise<DatabaseStats> => {
  try {
    console.log("Sending request to get database statistics");
    const response = await apiClient.get<DatabaseStats>("/database_stats");
    console.log("Received database statistics:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error retrieving database statistics:", error);
    throw error;
  }
};

/**
 * Generate an Earth Observation workflow based on a user-provided prompt.
 * This function sends a POST request to the '/generate_eo_workflow' endpoint.
 *
 * @param {string} prompt - The user's input prompt for generating the EO workflow.
 * @returns {Promise<{ workflow: string }>} - A promise that resolves to an object containing the generated workflow.
 *
 * @throws Will throw an error if the API request fails.
 *
 * @example
 * try {
 *   const result = await generateEOWorkflow("Create a workflow for monitoring deforestation using Sentinel-2 imagery");
 *   console.log(result.workflow);
 * } catch (error) {
 *   console.error("Failed to generate EO workflow:", error);
 * }
 */
export const generateEOWorkflow = async (
  prompt: string,
): Promise<{ workflow: string }> => {
  try {
    console.log(
      `Sending request to generate EO workflow with prompt: "${prompt}"`,
    );
    const response = await apiClient.post<{ workflow: string }>(
      "/generate_eo_workflow",
      { prompt },
    );
    console.log("Received EO workflow response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error generating EO workflow:", error);
    throw error;
  }
};

/**
 * Retrieve the Earth Observation graph data for visualization.
 * @returns {Promise<{ nodes: any[], links: any[], stats: any }>} - The graph data and statistics.
 */
export const getEOGraph = async (): Promise<{
  nodes: any[];
  links: any[];
  stats: any;
}> => {
  try {
    console.log("Sending request to get EO graph data");
    const response = await apiClient.get<{
      nodes: any[];
      links: any[];
      stats: any;
    }>("/eo_graph");
    console.log("Received EO graph data:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error retrieving EO graph data:", error);
    throw error;
  }
};

// export {
//   searchPapers,
//   getPaper,
//   getRecentPapers,
//   ping,
//   getInfo,
//   getAllPapers,
//   getDatabaseStats,
// };
