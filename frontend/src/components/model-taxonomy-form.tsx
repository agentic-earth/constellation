"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { InfoIcon } from "lucide-react";
import {
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
  EarthObservationModelTaxonomy,
  WeatherClimateModelTaxonomy,
  DatasetTaxonomy,
  FormData,
} from "@/types/paperTypes";

interface ModelTaxonomyFormProps {
  onSubmit: (formData: FormData) => void;
}

export function ModelTaxonomyForm({ onSubmit }: ModelTaxonomyFormProps) {
  const [formData, setFormData] = useState<FormData>({
    paper_type: PaperType.EARTH_OBSERVATION,
    paper_title: "",
    paper_url: "",
  });

  useEffect(() => {
    // Reset specific fields when paper_type changes
    setFormData((prevData) => ({
      ...prevData,
      spatial_scale: undefined,
      temporal_scale: undefined,
      application_readiness: undefined,
      model_type: undefined,
      architecture: undefined,
      input_data_types: [],
      output_data_type: undefined,
      spatial_resolution: undefined,
      temporal_resolution: undefined,
      satellite_data_sources: [],
      climate_weather_data_sources: [],
      processing_level: undefined,
    }));
  }, [formData.paper_type]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (name: string, value: any) => {
    setFormData({ ...formData, [name]: value });
  };

  const handleCheckboxChange = (
    name: string,
    value: string,
    checked: boolean
  ) => {
    setFormData((prevData) => {
      const currentValues =
        (prevData[name as keyof FormData] as string[]) || [];
      const newValues = checked
        ? [...currentValues, value]
        : currentValues.filter((v) => v !== value);
      return { ...prevData, [name]: newValues };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Form submitted:", formData);
    onSubmit(formData);
  };

  const renderCheckboxGroup = (
    name: string,
    options: string[],
    label: string
  ) => (
    <div className="space-y-2">
      <Label>{label}</Label>
      <div className="grid grid-cols-2 gap-2">
        {options.map((option) => (
          <div key={option} className="flex items-center space-x-2">
            <Checkbox
              id={`${name}-${option}`}
              checked={(
                (formData[name as keyof FormData] as string[]) || []
              ).includes(option)}
              onCheckedChange={(checked) =>
                handleCheckboxChange(name, option, checked as boolean)
              }
            />
            <Label htmlFor={`${name}-${option}`}>{option}</Label>
          </div>
        ))}
      </div>
    </div>
  );

  const renderSelectWithOther = (
    name: string,
    options: string[],
    label: string
  ) => (
    <div className="space-y-2">
      <Label htmlFor={name}>{label}</Label>
      <Select
        name={name}
        value={formData[name as keyof FormData] as string}
        onValueChange={(value) => handleSelectChange(name, value)}
      >
        <SelectTrigger>
          <SelectValue placeholder={`Select ${label.toLowerCase()}`} />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option} value={option}>
              {option}
            </SelectItem>
          ))}
          <SelectItem value="OTHER">Other</SelectItem>
        </SelectContent>
      </Select>
      {formData[name as keyof FormData] === "OTHER" && (
        <Input
          placeholder={`Specify other ${label.toLowerCase()}`}
          value={(formData[`${name}_other` as keyof FormData] as string) || ""}
          onChange={(e) => handleInputChange(e)}
          name={`${name}_other`}
        />
      )}
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Alert>
        <InfoIcon className="h-4 w-4" />
        <AlertTitle>Important</AlertTitle>
        <AlertDescription>
          Submitting a paper helps the community. Please ensure all information
          is accurate and up-to-date.
        </AlertDescription>
      </Alert>

      <Input
        name="paper_title"
        placeholder="Paper Title"
        value={formData.paper_title}
        onChange={handleInputChange}
        required
      />

      <Input
        name="paper_url"
        placeholder="Paper URL"
        type="url"
        value={formData.paper_url}
        onChange={handleInputChange}
        required
      />

      {renderSelectWithOther(
        "paper_type",
        Object.values(PaperType),
        "Paper Type"
      )}
      {renderSelectWithOther(
        "spatial_scale",
        Object.values(SpatialScale),
        "Spatial Scale"
      )}
      {renderSelectWithOther(
        "temporal_scale",
        Object.values(TemporalScale),
        "Temporal Scale"
      )}

      {formData.paper_type !== PaperType.DATASET && (
        <>
          {renderCheckboxGroup(
            "input_data_types",
            Object.values(InputDataType),
            "Input Data Types"
          )}
          {renderSelectWithOther(
            "output_data_type",
            Object.values(OutputDataType),
            "Output Data Type"
          )}
          {renderSelectWithOther(
            "model_type",
            Object.values(ModelType),
            "Model Type"
          )}
          {renderSelectWithOther(
            "architecture",
            Object.values(Architecture),
            "Architecture"
          )}
          {renderSelectWithOther(
            "application_readiness",
            Object.values(ApplicationReadiness),
            "Application Readiness"
          )}
          {renderSelectWithOther(
            "spatial_resolution",
            Object.values(SpatialResolution),
            "Spatial Resolution"
          )}
          {renderSelectWithOther(
            "temporal_resolution",
            Object.values(TemporalResolution),
            "Temporal Resolution"
          )}
          {renderSelectWithOther(
            "processing_level",
            Object.values(ProcessingLevel),
            "Processing Level"
          )}
        </>
      )}

      {formData.paper_type === PaperType.EARTH_OBSERVATION &&
        renderCheckboxGroup(
          "satellite_data_sources",
          Object.values(SatelliteSource),
          "Satellite Data Sources"
        )}

      {formData.paper_type === PaperType.WEATHER_CLIMATE &&
        renderCheckboxGroup(
          "climate_weather_data_sources",
          Object.values(ClimateWeatherDataSource),
          "Climate/Weather Data Sources"
        )}

      <Button type="submit" className="w-full">
        Submit Paper
      </Button>
    </form>
  );
}
