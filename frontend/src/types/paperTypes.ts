// Enums
enum PaperType {
  WEATHER_CLIMATE = "Weather/Climate Model",
  EARTH_OBSERVATION = "Earth Observation Model",
  DATASET = "Dataset",
  OTHER = "Other",
}

enum SpatialScale {
  LOCAL = "Local",
  REGIONAL = "Regional",
  NATIONAL = "National",
  CONTINENTAL = "Continental",
  GLOBAL = "Global",
  NA = "N/A",
}

enum TemporalScale {
  STATIC = "Static",
  DAILY = "Daily",
  WEEKLY = "Weekly",
  MONTHLY = "Monthly",
  ANNUAL = "Annual",
  DECADAL = "Decadal",
  MULTI_DECADAL = "Multi-decadal",
  NA = "N/A",
}

enum ApplicationReadiness {
  THEORETICAL = "Theoretical",
  EXPERIMENTAL = "Experimental",
  PROTOTYPE = "Prototype",
  OPERATIONAL = "Operational",
  NA = "N/A",
}

enum ModelType {
  VISION = "Vision",
  CLIMATE = "Climate",
  WEATHER = "Weather",
  NA = "N/A",
}

enum Architecture {
  CNN = "Convolutional Neural Network",
  RNN = "Recurrent Neural Network",
  LSTM = "Long Short-Term Memory",
  TRANSFORMER = "Transformer",
  VISION_TRANSFORMER = "Vision Transformer",
  GAN = "Generative Adversarial Network",
  DIFFUSION_MODEL = "Diffusion Model",
  GNN = "Graph Neural Network",
  MLP = "Multi-Layer Perceptron",
  DECISION_TREE = "Decision Tree",
  RANDOM_FOREST = "Random Forest",
  ENSEMBLE = "Ensemble Method",
  UNET = "U-Net",
  AUTOENCODER = "Autoencoder",
  OTHER = "Other",
  NA = "N/A",
}

enum InputDataType {
  OPTICAL = "Optical",
  SAR = "SAR",
  LIDAR = "LiDAR",
  HYPERSPECTRAL = "Hyperspectral",
  CLIMATE = "Climate",
  WEATHER = "Weather",
  MICROWAVE = "Microwave",
  THERMAL = "Thermal",
  MULTISPECTRAL = "Multispectral",
  OTHER = "Other",
}

enum OutputDataType {
  CLASSIFICATION = "Classification",
  REGRESSION = "Regression",
  OBJECT_DETECTION = "Object Detection",
  SEGMENTATION = "Segmentation",
  TIME_SERIES = "Time Series",
  CHANGE_DETECTION = "Change Detection",
  FORECASTING = "Forecasting",
  ANOMALY_DETECTION = "Anomaly Detection",
  NA = "N/A",
}

enum SpatialResolution {
  EXTREMELY_HIGH = "Extremely High (<0.1m)",
  VERY_HIGH = "Very High (0.1-1m)",
  HIGH = "High (1-5m)",
  MEDIUM_HIGH = "Medium-High (5-10m)",
  MEDIUM = "Medium (10-30m)",
  MEDIUM_LOW = "Medium-Low (30-100m)",
  LOW = "Low (100-250m)",
  VERY_LOW = "Very Low (250-1000m)",
  EXTREMELY_LOW = "Extremely Low (>1000m)",
  VARIABLE = "Variable Resolution",
  CUSTOM = "Custom Resolution",
  NA = "N/A",
}

enum TemporalResolution {
  HOURLY = "Hourly",
  DAILY = "Daily",
  WEEKLY = "Weekly",
  BIWEEKLY = "Bi-weekly",
  MONTHLY = "Monthly",
  ANNUAL = "Annual",
  NA = "N/A",
}

enum SatelliteSource {
  LANDSAT_1 = "Landsat 1",
  LANDSAT_2 = "Landsat 2",
  LANDSAT_3 = "Landsat 3",
  LANDSAT_4 = "Landsat 4",
  LANDSAT_5 = "Landsat 5",
  LANDSAT_6 = "Landsat 6",
  LANDSAT_7 = "Landsat 7",
  LANDSAT_8 = "Landsat 8",
  LANDSAT_9 = "Landsat 9",
  SENTINEL_1A = "Sentinel-1A",
  SENTINEL_1B = "Sentinel-1B",
  SENTINEL_2A = "Sentinel-2A",
  SENTINEL_2B = "Sentinel-2B",
  SENTINEL_3A = "Sentinel-3A",
  SENTINEL_3B = "Sentinel-3B",
  SENTINEL_5P = "Sentinel-5P",
  SENTINEL_1 = "Sentinel-1",
  SENTINEL_2 = "Sentinel-2",
  SENTINEL_3 = "Sentinel-3",
  SENTINEL_5 = "Sentinel-5",
  TERRA_MODIS = "Terra MODIS",
  AQUA_MODIS = "Aqua MODIS",
  GOES_13 = "GOES-13",
  GOES_14 = "GOES-14",
  GOES_15 = "GOES-15",
  GOES_16 = "GOES-16",
  GOES_17 = "GOES-17",
  GOES_18 = "GOES-18",
  NOAA_15 = "NOAA-15",
  NOAA_18 = "NOAA-18",
  NOAA_19 = "NOAA-19",
  NOAA_20 = "NOAA-20",
  SMAP = "SMAP",
  ICESAT_2 = "ICESat-2",
  GRACE = "GRACE",
  GRACE_FO = "GRACE Follow-On",
  TRMM = "TRMM",
  GPM = "GPM",
  TERRA = "Terra",
  AQUA = "Aqua",
  AURA = "Aura",
  SUOMI_NPP = "Suomi NPP",
  WORLDVIEW_1 = "WorldView-1",
  WORLDVIEW_2 = "WorldView-2",
  WORLDVIEW_3 = "WorldView-3",
  WORLDVIEW_4 = "WorldView-4",
  GEOEYE_1 = "GeoEye-1",
  PLANETSCOPE = "PlanetScope",
  RAPIDEYE = "RapidEye",
  PLEIADES = "Pleiades",
  SPOT_6 = "SPOT-6",
  SPOT_7 = "SPOT-7",
  RADARSAT_1 = "RADARSAT-1",
  RADARSAT_2 = "RADARSAT-2",
  TERRASAR_X = "TerraSAR-X",
  TANDEM_X = "TanDEM-X",
  ALOS_1 = "ALOS-1",
  ALOS_2 = "ALOS-2",
  COSMO_SKYMED = "COSMO-SkyMed",
  ICEYE = "ICEYE",
  SAR = "Other Radar",
  ENVISAT = "Envisat",
  ERS_1 = "ERS-1",
  ERS_2 = "ERS-2",
  SRTM = "SRTM",
  EOSDA = "EOSDA",
  PROBA_V = "PROBA-V",
  METOP_A = "MetOp-A",
  METOP_B = "MetOp-B",
  METOP_C = "MetOp-C",
  HIMAWARI_8 = "Himawari-8",
  HIMAWARI_9 = "Himawari-9",
  FY_3 = "FY-3",
  FY_4 = "FY-4",
  NAIP = "NAIP",
  NA = "N/A",
  CMIP6 = 'CMIP6',
}

enum ClimateWeatherDataSource {
  ERA5 = "ERA5",
  CMIP6 = "CMIP6",
  NCEP_REANALYSIS = "NCEP Reanalysis",
  MERRA2 = "MERRA-2",
  GLDAS = "GLDAS",
  GHCN = "GHCN",
  ECMWF = "ECMWF",
  NOAA_CFS = "NOAA CFS",
  NA = "N/A",
}

enum ProcessingLevel {
  LEVEL_0 = "Level 0",
  LEVEL_1 = "Level 1",
  LEVEL_2 = "Level 2",
  LEVEL_3 = "Level 3",
  LEVEL_4 = "Level 4",
  NA = "N/A",
}

// Interfaces
interface SearchQuery {
  keywords?: string[];
  paper_type?: PaperType;
  date_range?: [string, string];
  taxonomy_filters?: {
    general?: Record<string, any>;
    earth_observation?: Record<string, any>;
    weather_climate?: Record<string, any>;
    dataset?: Record<string, any>;
  };
  limit: number;
  offset: number;
  searchTerm?: string; 
}

interface FullPaper {
  id: string;
  title: string;
  abstract: string;
  authors: string[];
  publication_date: string;
  url: string;
  pdf_url?: string;
  paper_type: PaperType;
  keywords: string[];
  metadata: Record<string, any>;
  block_type: string;
}

interface SearchResult {
  papers: FullPaper[];
  total_count: number;
  page: number;
  total_pages: number;
  query: SearchQuery;
}

interface ModelCharacteristics {
  is_stochastic: boolean;
  is_deterministic: boolean;
  is_multi_modal: boolean;
  is_foundation_model: boolean;
  is_physics_informed: boolean;
}

interface GeneralTaxonomy {
  paper_id: string;
  created_at: string;
  updated_at: string;
  version: number;
  code_url?: string;
  paper_type: PaperType;
  application_areas: string[];
  keywords: string[];
  spatial_scale: SpatialScale;
  temporal_scale: TemporalScale;
  application_readiness: ApplicationReadiness;
}

interface ModelTaxonomyBase extends GeneralTaxonomy {
  model_type: ModelType;
  architecture: Architecture;
  model_characteristics: ModelCharacteristics;
  input_data_types: InputDataType[];
  output_data_type: OutputDataType;
  spatial_resolution: SpatialResolution;
  temporal_resolution: TemporalResolution;
}

interface EarthObservationModelTaxonomy extends ModelTaxonomyBase {
  satellite_data_sources: SatelliteSource[];
  processing_level: ProcessingLevel;
}

interface WeatherClimateModelTaxonomy extends ModelTaxonomyBase {
  climate_weather_data_sources: ClimateWeatherDataSource[];
}

interface DatasetTaxonomy extends GeneralTaxonomy {
  satellite_data_sources: SatelliteSource[];
  climate_weather_data_sources: ClimateWeatherDataSource[];
  spatial_resolution: SpatialResolution;
  temporal_resolution: TemporalResolution;
  processing_level: ProcessingLevel;
}

type Taxonomy = {
  general: GeneralTaxonomy;
  specific?:
    | EarthObservationModelTaxonomy
    | WeatherClimateModelTaxonomy
    | DatasetTaxonomy;
};

interface DatabaseStats {
  total_papers: number;
  papers_by_type: Record<PaperType, number>;
}

interface BasePaperData {
  paper_title: string;
  paper_url: string;
  paper_type: PaperType;
}

export type FormData = Partial<
  BasePaperData &
    (
      | EarthObservationModelTaxonomy
      | WeatherClimateModelTaxonomy
      | DatasetTaxonomy
    )
>;

export {
  PaperType,
  SpatialScale,
  TemporalScale,
  ApplicationReadiness,
  ModelType,
  Architecture,
  InputDataType,
  OutputDataType,
  SpatialResolution,
  TemporalResolution,
  SatelliteSource,
  ClimateWeatherDataSource,
  ProcessingLevel,
};

export type {
  DatabaseStats,
  SearchQuery,
  FullPaper,
  SearchResult,
  ModelCharacteristics,
  GeneralTaxonomy,
  ModelTaxonomyBase,
  EarthObservationModelTaxonomy,
  WeatherClimateModelTaxonomy,
  DatasetTaxonomy,
  Taxonomy,
};
