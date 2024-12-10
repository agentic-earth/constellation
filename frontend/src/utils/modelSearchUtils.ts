import { PaperType, SearchQuery } from "@/types/paperTypes";

export const getPaperType = (category: string): PaperType => {
  switch (category) {
    case "earth-observation":
      return PaperType.EARTH_OBSERVATION;
    case "climate-weather":
      return PaperType.WEATHER_CLIMATE;
    case "datasets":
      return PaperType.DATASET;
    default:
      return PaperType.EARTH_OBSERVATION;
  }
};

export const getItemsPerPage = (width: number): number => {
  if (width >= 1536) return 12; // 2xl
  if (width >= 1280) return 9; // xl
  if (width >= 1024) return 6; // lg
  if (width >= 768) return 4; // md
  return 2; // sm
};

export const updateSearchQuery = (
  prevQuery: SearchQuery,
  updates: Partial<SearchQuery>,
): SearchQuery => {
  return {
    ...prevQuery,
    ...updates,
    offset: 0, // Reset to first page
  };
};
