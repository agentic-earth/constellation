# backend/models/taxonomy.py

"""
Taxonomy Models Module

This module defines the taxonomy-related Pydantic models using Pydantic v2.
It includes base classes and specific taxonomy schemas for different paper types.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from uuid import UUID
from datetime import datetime


# -------------------
# Enum Definitions
# -------------------

class PaperType(str, Enum):
    WEATHER_CLIMATE = "Weather/Climate Model"
    EARTH_OBSERVATION = "Earth Observation Model"
    DATASET = "Dataset"
    OTHER = "Other"

class InputDataType(str, Enum):
    OPTICAL = "Optical"
    SAR = "SAR"
    LIDAR = "LiDAR"
    HYPERSPECTRAL = "Hyperspectral"
    CLIMATE = "Climate"
    WEATHER = "Weather"
    MICROWAVE = "Microwave"
    THERMAL = "Thermal"
    MULTISPECTRAL = "Multispectral"
    OTHER = "Other"

class ApplicationArea(str, Enum):
    LAND_USE_LAND_COVER = "Land Use and Land Cover"
    AGRICULTURE_FOOD_SECURITY = "Agriculture and Food Security"
    FORESTRY_ECOSYSTEM = "Forestry and Ecosystem Management"
    URBAN_RURAL_DEVELOPMENT = "Urban and Rural Development"
    DISASTER_RISK_MANAGEMENT = "Disaster Risk Management"
    COASTAL_MARINE_RESOURCES = "Coastal and Marine Resources"
    CLIMATE_ATMOSPHERIC_SCIENCE = "Climate and Atmospheric Science"
    CRYOSPHERE_POLAR_STUDIES = "Cryosphere and Polar Studies"
    WATER_RESOURCES_HYDROLOGY = "Water Resources and Hydrology"
    BIODIVERSITY_CONSERVATION = "Biodiversity and Conservation"
    ENERGY_RESOURCES = "Energy Resources"
    GEOLOGY_GEOHAZARDS = "Geology and Geohazards"
    HEALTH_EPIDEMIOLOGY = "Health and Epidemiology"
    TRANSPORTATION_INFRASTRUCTURE = "Transportation and Infrastructure"
    SOCIOECONOMIC_ANALYSIS = "Socioeconomic Analysis"
    NATIONAL_SECURITY_DEFENSE = "National Security and Defense"
    ENVIRONMENTAL_MONITORING = "Environmental Monitoring and Protection"
    NATURAL_RESOURCE_MANAGEMENT = "Natural Resource Management"
    SUSTAINABLE_DEVELOPMENT = "Sustainable Development"
    CULTURAL_HERITAGE_PRESERVATION = "Cultural Heritage Preservation"
    FIRE_MANAGEMENT = "Fire Management and Monitoring"
    OCEAN_SCIENCE = "Ocean Science and Oceanography"
    CLOUD_STUDIES = "Cloud Studies and Atmospheric Dynamics"
    WEATHER_FORECASTING = "Weather Forecasting and Prediction"
    CLIMATE_CHANGE_MODELING = "Climate Change Modeling and Projections"
    GENERAL = "General"
    NA = "N/A"

class SatelliteSource(str, Enum):
    # Landsat series
    LANDSAT_1 = "Landsat 1"
    LANDSAT_2 = "Landsat 2"
    LANDSAT_3 = "Landsat 3"
    LANDSAT_4 = "Landsat 4"
    LANDSAT_5 = "Landsat 5"
    LANDSAT_6 = "Landsat 6"
    LANDSAT_7 = "Landsat 7"
    LANDSAT_8 = "Landsat 8"
    LANDSAT_9 = "Landsat 9"
    
    # Sentinel series
    SENTINEL_1A = "Sentinel-1A"
    SENTINEL_1B = "Sentinel-1B"
    SENTINEL_2A = "Sentinel-2A"
    SENTINEL_2B = "Sentinel-2B"
    SENTINEL_3A = "Sentinel-3A"
    SENTINEL_3B = "Sentinel-3B"
    SENTINEL_5P = "Sentinel-5P"
    SENTINEL_1 = "Sentinel-1"
    SENTINEL_2 = "Sentinel-2"
    SENTINEL_3 = "Sentinel-3"
    SENTINEL_5 = "Sentinel-5"

    # MODIS
    TERRA_MODIS = "Terra MODIS"
    AQUA_MODIS = "Aqua MODIS"
    
    # GOES series
    GOES_13 = "GOES-13"
    GOES_14 = "GOES-14"
    GOES_15 = "GOES-15"
    GOES_16 = "GOES-16"
    GOES_17 = "GOES-17"
    GOES_18 = "GOES-18"
    
    # NOAA series
    NOAA_15 = "NOAA-15"
    NOAA_18 = "NOAA-18"
    NOAA_19 = "NOAA-19"
    NOAA_20 = "NOAA-20"
    
    # Other NASA satellites
    SMAP = "SMAP"
    ICESAT_2 = "ICESat-2"
    GRACE = "GRACE"
    GRACE_FO = "GRACE Follow-On"
    TRMM = "TRMM"
    GPM = "GPM"
    TERRA = "Terra"
    AQUA = "Aqua"
    AURA = "Aura"
    SUOMI_NPP = "Suomi NPP"
    
    # Commercial satellites
    WORLDVIEW_1 = "WorldView-1"
    WORLDVIEW_2 = "WorldView-2"
    WORLDVIEW_3 = "WorldView-3"
    WORLDVIEW_4 = "WorldView-4"
    GEOEYE_1 = "GeoEye-1"
    PLANETSCOPE = "PlanetScope"
    RAPIDEYE = "RapidEye"
    PLEIADES = "Pleiades"
    SPOT_6 = "SPOT-6"
    SPOT_7 = "SPOT-7"
    
    # Radar satellites
    RADARSAT_1 = "RADARSAT-1"
    RADARSAT_2 = "RADARSAT-2"
    TERRASAR_X = "TerraSAR-X"
    TANDEM_X = "TanDEM-X"
    ALOS_1 = "ALOS-1"
    ALOS_2 = "ALOS-2"
    COSMO_SKYMED = "COSMO-SkyMed"
    ICEYE = "ICEYE"
    SAR = "Other Radar"

    # Other satellites
    ENVISAT = "Envisat"
    ERS_1 = "ERS-1"
    ERS_2 = "ERS-2"
    SRTM = "SRTM"
    EOSDA = "EOSDA"
    PROBA_V = "PROBA-V"
    METOP_A = "MetOp-A"
    METOP_B = "MetOp-B"
    METOP_C = "MetOp-C"
    HIMAWARI_8 = "Himawari-8"
    HIMAWARI_9 = "Himawari-9"
    FY_3 = "FY-3"
    FY_4 = "FY-4"

    NAIP = "NAIP"
    NA = "N/A"



class SpatialResolution(str, Enum):
    EXTREMELY_HIGH = "Extremely High (<0.1m)"
    VERY_HIGH = "Very High (0.1-1m)"
    HIGH = "High (1-5m)"
    MEDIUM_HIGH = "Medium-High (5-10m)"
    MEDIUM = "Medium (10-30m)"
    MEDIUM_LOW = "Medium-Low (30-100m)"
    LOW = "Low (100-250m)"
    VERY_LOW = "Very Low (250-1000m)"
    EXTREMELY_LOW = "Extremely Low (>1000m)"
    VARIABLE = "Variable Resolution"
    CUSTOM = "Custom Resolution"
    NA = "N/A"


class TemporalResolution(str, Enum):
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Bi-weekly"
    MONTHLY = "Monthly"
    ANNUAL = "Annual"
    NA = "N/A"


class SpatialScale(str, Enum):
    LOCAL = "Local"
    REGIONAL = "Regional"
    NATIONAL = "National"
    CONTINENTAL = "Continental"
    GLOBAL = "Global"
    NA = "N/A"

class TemporalScale(str, Enum):
    STATIC = "Static"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    ANNUAL = "Annual"
    DECADAL = "Decadal"
    MULTI_DECADAL = "Multi-decadal"
    NA = "N/A"

class ApplicationReadiness(str, Enum):
    THEORETICAL = "Theoretical"
    EXPERIMENTAL = "Experimental"
    PROTOTYPE = "Prototype"
    OPERATIONAL = "Operational"
    NA = "N/A"

class ModelType(str, Enum):
    VISION = "Vision"
    CLIMATE = "Climate"
    WEATHER = "Weather"
    NA = "N/A"

class Architecture(str, Enum):
    CNN = "CNN"
    RNN = "RNN"
    LSTM = "LSTM"
    TRANSFORMER = "Transformer"
    VISION_TRANSFORMER = "Vision Transformer"
    GAN = "Generative Adversarial Network"
    DIFFUSION_MODEL = "Diffusion Model"
    GNN = "Graph Neural Network"
    MLP = "Multi-Layer Perceptron"
    DECISION_TREE = "Decision Tree"
    RANDOM_FOREST = "Random Forest"
    GRADIENT_BOOSTING = "Gradient Boosting"
    SVM = "Support Vector Machine"
    ENSEMBLE = "Ensemble Method"
    UNET = "U-Net"
    AUTOENCODER = "Autoencoder"
    VAE = "Variational Autoencoder"
    OTHER = "Other"
    NA = "N/A"

class ProcessingLevel(str, Enum):
    LEVEL_0 = "Level 0"
    LEVEL_1 = "Level 1"
    LEVEL_2 = "Level 2"
    LEVEL_3 = "Level 3"
    LEVEL_4 = "Level 4"
    NA = "N/A"

class DependencyTypeEnum(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"

class OutputDataType(str, Enum):
    CLASSIFICATION = "Classification"
    REGRESSION = "Regression"
    OBJECT_DETECTION = "Object Detection"
    SEGMENTATION = "Segmentation"
    TIME_SERIES = "Time Series"
    CHANGE_DETECTION = "Change Detection"
    FORECASTING = "Forecasting"
    ANOMALY_DETECTION = "Anomaly Detection"
    NA = "N/A"


class ModelCharacteristics(BaseModel):
    is_stochastic: bool = False
    is_deterministic: bool = True
    is_multi_modal: bool = False
    is_foundation_model: bool = False
    is_physics_informed: bool = False

class Architecture(str, Enum):
    # General architectures
    CNN = "Convolutional Neural Network"
    RNN = "Recurrent Neural Network"
    LSTM = "Long Short-Term Memory"
    GRU = "Gated Recurrent Unit"
    TRANSFORMER = "Transformer"
    VISION_TRANSFORMER = "Vision Transformer"
    GAN = "Generative Adversarial Network"
    DIFFUSION_MODEL = "Diffusion Model"
    GNN = "Graph Neural Network"
    MLP = "Multi-Layer Perceptron"
    DECISION_TREE = "Decision Tree"
    RANDOM_FOREST = "Random Forest"
    GRADIENT_BOOSTING = "Gradient Boosting"
    SVM = "Support Vector Machine"
    ENSEMBLE = "Ensemble Method"
    UNET = "U-Net"
    AUTOENCODER = "Autoencoder"
    VAE = "Variational Autoencoder"

    OTHER = "Other"
    NA = "N/A"



class PaperType(str, Enum):
    WEATHER_CLIMATE = "Weather/Climate Model"
    EARTH_OBSERVATION = "Earth Observation Model"
    DATASET = "Dataset"
    OTHER = "Other"

class PaperTypeModel(BaseModel):
    paper_type: PaperType

class ScrapedPaper(BaseModel):
    """
    Represents the initial data scraped from a source.
    This object is immutable once created.
    """
    id: str = Field(..., description="Unique identifier for the paper")
    title: str = Field(..., description="Title of the paper")
    abstract: str = Field(..., description="Abstract of the paper")
    authors: List[str] = Field(..., description="List of authors")
    publication_date: datetime = Field(..., description="Date of publication")
    url: str = Field(..., description="URL to the paper")
    pdf_url: Optional[str] = Field(None, description="URL to the paper's PDF file")

    class Config:
        frozen = True  # Makes the object immutable

class EnrichedPaper(BaseModel):
    """
    Represents a paper after LLM processing.
    This builds upon ScrapedPaper with additional fields.
    """
    scraped_data: ScrapedPaper
    paper_type: Optional[PaperType] = Field(None, description="Type of the research paper")
    #keywords: Optional[List[str]] = Field(None, description="List of keywords")
    #metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata storage")

    @property
    def id(self) -> str:
        return self.scraped_data.id

    @property
    def title(self) -> str:
        return self.scraped_data.title

    @property
    def abstract(self) -> str:
        return self.scraped_data.abstract

    @property
    def authors(self) -> List[str]:
        return self.scraped_data.authors

    @property
    def publication_date(self) -> datetime:
        return self.scraped_data.publication_date

    @property
    def url(self) -> str:
        return self.scraped_data.url

    @property
    def pdf_url(self) -> Optional[str]:
        return self.scraped_data.pdf_url

class FullPaper(BaseModel):
    """
    Represents the final, complete paper object.
    This is created once all processing is done.
    """
    id: str = Field(..., description="Unique identifier for the paper")
    title: str = Field(..., description="Title of the paper")
    abstract: str = Field(..., description="Abstract of the paper")
    authors: List[str] = Field(..., description="List of authors")
    publication_date: datetime = Field(..., description="Date of publication")
    url: str = Field(..., description="URL to the paper")
    pdf_url: Optional[str] = Field(None, description="URL to the paper's PDF file")

    paper_type: PaperType = Field(..., description="Type of the research paper")
    keywords: List[str] = Field(..., description="List of keywords")
    metadata: Dict[str, Any] = Field(..., description="Flexible metadata storage")

    @classmethod
    def from_enriched(cls, enriched: EnrichedPaper) -> 'FullPaper':
        if enriched.paper_type is None or enriched.keywords is None:
            raise ValueError("EnrichedPaper must have paper_type and keywords to create a FullPaper")
        return cls(
            id=enriched.scraped_data.id,
            title=enriched.scraped_data.title,
            abstract=enriched.scraped_data.abstract,
            authors=enriched.scraped_data.authors,
            publication_date=enriched.scraped_data.publication_date,
            url=enriched.scraped_data.url,
            pdf_url=enriched.scraped_data.pdf_url,
            paper_type=enriched.paper_type,
            keywords=enriched.keywords,
            metadata=enriched.metadata
        )




# -------------------
# Model Definitions
# -------------------

class ModelCharacteristics(BaseModel):
    is_stochastic: bool = Field(default=False, description="Indicates if the model is stochastic.")
    is_deterministic: bool = Field(default=True, description="Indicates if the model is deterministic.")
    is_multi_modal: bool = Field(default=False, description="Indicates if the model is multi-modal.")
    is_foundation_model: bool = Field(default=False, description="Indicates if the model is a foundation model.")
    is_physics_informed: bool = Field(default=False, description="Indicates if the model is physics-informed.")

    model_config = ConfigDict(from_attributes=True)

class TaxonomyBase(BaseModel):
    paper_id: str = Field(..., description="ID of the associated paper.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of taxonomy creation.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last update.")
    version: int = Field(default=1, description="Version number of the taxonomy.")
    code_url: Optional[str] = Field(None, description="URL to the code repository.")

    model_config = ConfigDict(from_attributes=True)

class GeneralTaxonomy(TaxonomyBase):
    paper_type: PaperType = Field(..., description="Type of the research paper.")
    application_areas: List[ApplicationArea] = Field(..., description="List of application areas.")
    keywords: List[str] = Field(..., description="List of keywords.")
    spatial_scale: SpatialScale = Field(..., description="Spatial scale of the study.")
    temporal_scale: TemporalScale = Field(..., description="Temporal scale of the study.")
    application_readiness: ApplicationReadiness = Field(..., description="Readiness level of the application or method.")

    model_config = ConfigDict(from_attributes=True)

class ModelTaxonomyBase(GeneralTaxonomy):
    model_type: ModelType = Field(..., description="Type of the model.")
    architecture: Architecture = Field(..., description="Architecture of the implemented model.")
    model_characteristics: ModelCharacteristics = Field(..., description="Characteristics of the model.")
    input_data_types: List[InputDataType] = Field(..., description="Types of input data used.")
    output_data_type: OutputDataType = Field(..., description="Type of output data produced.")
    spatial_resolution: SpatialResolution = Field(..., description="Spatial resolution of the model.")
    temporal_resolution: TemporalResolution = Field(..., description="Temporal resolution of the model.")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class EarthObservationModelTaxonomy(ModelTaxonomyBase):
    satellite_data_sources: List[SatelliteSource] = Field(..., description="Satellite data sources used.")
    processing_level: ProcessingLevel = Field(..., description="Processing level of input data.")

    model_config = ConfigDict(from_attributes=True)

class WeatherClimateModelTaxonomy(ModelTaxonomyBase):
    climate_weather_data_sources: List["ClimateWeatherDataSource"] = Field(..., description="Climate/weather data sources used.")

    model_config = ConfigDict(from_attributes=True)

class DatasetTaxonomy(GeneralTaxonomy):
    satellite_data_sources: List[SatelliteSource] = Field(..., description="Satellite data sources.")
    climate_weather_data_sources: List["ClimateWeatherDataSource"] = Field(..., description="Climate/weather data sources.")
    spatial_resolution: SpatialResolution = Field(..., description="Spatial resolution of the data.")
    temporal_resolution: TemporalResolution = Field(..., description="Temporal resolution of the data.")
    processing_level: ProcessingLevel = Field(..., description="Processing level of the data.")

    model_config = ConfigDict(from_attributes=True)

class Taxonomy(BaseModel):
    general: GeneralTaxonomy
    specific: Optional[Union[EarthObservationModelTaxonomy, WeatherClimateModelTaxonomy, DatasetTaxonomy]] = Field(None, description="Specific taxonomy based on paper type.")

    model_config = ConfigDict(from_attributes=True)

# Mapping between PaperType and Taxonomy classes
PAPER_TYPE_TO_TAXONOMY: Dict[PaperType, type] = {
    PaperType.WEATHER_CLIMATE: WeatherClimateModelTaxonomy,
    PaperType.EARTH_OBSERVATION: EarthObservationModelTaxonomy,
    PaperType.DATASET: DatasetTaxonomy,
    PaperType.OTHER: GeneralTaxonomy  # Assuming GeneralTaxonomy for 'Other'
}

class TaxonomyFilter(BaseModel):
    general: Optional[Dict[str, Any]] = Field(None, description="Filters for GeneralTaxonomy fields.")
    earth_observation: Optional[Dict[str, Any]] = Field(None, description="Filters for EarthObservationModelTaxonomy fields.")
    weather_climate: Optional[Dict[str, Any]] = Field(None, description="Filters for WeatherClimateModelTaxonomy fields.")
    dataset: Optional[Dict[str, Any]] = Field(None, description="Filters for DatasetTaxonomy fields.")

    model_config = ConfigDict(from_attributes=True)

class DatabaseStats(BaseModel):
    total_papers: int = Field(..., description="Total number of papers in the database.")
    papers_by_type: Dict[PaperType, int] = Field(..., description="Number of papers categorized by type.")

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator
from dateutil import parser as date_parser

class SearchQuery(BaseModel):
    """
    Represents a search query for filtering papers.

    Attributes:
        keywords (Optional[List[str]]): List of keywords to search for in title and abstract.
        paper_type (Optional[PaperType]): Type of paper to filter by.
        date_range (Optional[Tuple[datetime, datetime]]): Date range to filter papers by publication date.
        taxonomy_filters (Optional[Dict[str, Any]]): Filters for taxonomy fields.
        limit (int): Maximum number of results to return.
        offset (int): Number of results to skip for pagination.

    Example:
        ```python
        query = SearchQuery(
            keywords=["climate change"],
            paper_type=PaperType.EARTH_OBSERVATION,
            date_range=(datetime(2020, 1, 1), datetime(2023, 12, 31)),
            taxonomy_filters={
                "satellite_data_sources": [SatelliteSource.SENTINEL_2],
                "application_areas": [ApplicationArea.CLIMATE_ATMOSPHERIC_SCIENCE],
                "architecture": Architecture.CNN
            },
            limit=10,
            offset=0
        )
        ```
    """
    keywords: Optional[List[str]] = None
    paper_type: Optional[PaperType] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    taxonomy_filters: Optional[Dict[str, Any]] = None
    limit: int = Field(default=10)
    offset: int = Field(default=0)

    @field_validator('date_range', mode='before')
    @classmethod
    def parse_date_range(cls, v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            try:
                return tuple(cls.parse_datetime(date) for date in v)
            except ValueError as e:
                raise ValueError(f"Invalid date format in date_range: {str(e)}")
        return v

    @staticmethod
    def parse_datetime(value):
        if isinstance(value, datetime):
            return value.replace(tzinfo=timezone.utc)
        if isinstance(value, str):
            try:
                # Use dateutil.parser to handle ISO 8601 formats
                dt = date_parser.isoparse(value)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                raise ValueError(f"Unable to parse date string: {value}")
        raise ValueError(f"Unsupported date type: {type(value)}")

    model_config = ConfigDict(
        json_serializers={
            datetime: lambda v: v.isoformat()
        }
    )

class SearchResult(BaseModel):
    papers: List[FullPaper] = Field(..., description="List of full papers matching the search criteria")
    total_count: int = Field(..., description="Total number of papers matching the search criteria")
    page: int = Field(..., description="Current page number")
    total_pages: int = Field(..., description="Total number of pages available")
    query: SearchQuery = Field(..., description="The original search query")

    model_config = ConfigDict(arbitrary_types_allowed=True)

class EOWorkflowRequest(BaseModel):
    prompt: str

__all__ = [
    "ModelType", "Architecture", "ModelCharacteristics",
    "TaxonomyBase", "GeneralTaxonomy", "ModelTaxonomyBase",
    "EarthObservationModelTaxonomy", "WeatherClimateModelTaxonomy",
    "DatasetTaxonomy", "Taxonomy",
    "SearchQuery", "SearchResult",
    "PAPER_TYPE_TO_TAXONOMY", "PaperTypeModel"
]