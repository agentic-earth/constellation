import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function Features() {
  return (
    <section
      id="features"
      className="w-full py-12 md:py-24 lg:py-32 flex justify-center bg-gradient-to-br from-primary to-primary/90"
    >
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-8 text-center mb-16">
          <div className="inline-block rounded-lg bg-primary-foreground/20 px-3 py-1 text-sm text-black">
            building blocks for agentic earth system research
          </div>
          <div className="max-w-[900px] bg-black/80 rounded-2xl p-6 relative overflow-hidden group">
            <div className="absolute inset-0 bg-black/90 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-in-out"></div>
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl text-center px-4 text-primary relative z-10">
              An Evolving Open-Source Library of Earth System Models
            </h2>
          </div>
          <p className="text-black md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed text-center max-w-[900px]">
            Access, publish, and run the latest research models. Scale your
            research to the next-level with a professional toolkit that enables
            large ensemble analysis and AI-model intercomparison.
          </p>
        </div>
        <div className="w-full flex flex-col items-center">
          <Card className="w-full max-w-4xl bg-primary-foreground/10 rounded-3xl overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-primary-foreground/20 group">
            <CardHeader className="flex flex-col items-center gap-4 py-8 md:flex-row md:justify-between">
              <div className="space-y-2 text-center md:text-left">
                <CardTitle className="text-3xl font-bold text-black">
                  AI Models from Start-to-Finish
                </CardTitle>
                <CardDescription className="text-black/80">
                  Empowering users to host and connect their geospatial models.
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="text-black border-black hover:bg-black/10 transition-all duration-300"
              >
                <ExploreIcon className="mr-2 h-4 w-4" />
                Explore the Platform
              </Button>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-8 md:grid-cols-3">
              <FeatureCard
                icon={<SatelliteIcon />}
                title="Data Ingestion"
                description="Programmatically ingest 200+ data sources through our unified gateway."
                linkText="Host your data source"
              />
              <FeatureCard
                icon={<AssimilatorIcon />}
                title="Geospatial Foundation Models"
                description="Assimilate multi-modal EO data into common vector embeddings through popular GFMs."
                linkText="Host your geospatial model"
              />
              <FeatureCard
                icon={<CloudSunRainIcon />}
                title="Earth Simulation"
                description="Neural Climate + Weather Simulations from the latest research labs."
                linkText="Host your climate model"
              />
              <FeatureCard
                icon={<EnsembleIcon />}
                title="AI Ensemble Toolkit"
                description="Easily connect data streams to AI models and run ensembles in one line."
                linkText="Optimize your dynamics"
              />
              <FeatureCard
                icon={<VectorDatabaseIcon />}
                title="Climate Vector Database"
                description="Cloud-optimized ChromaDB backend to store and query high dimensional model outputs in a STAC compliant VDB."
                linkText="Train Downstream models on VDB"
              />
              <FeatureCard
                icon={<RobotIcon />}
                title="Reinforcement Learning"
                description="Gym Adherent Env-Wrappers for Neural Climate Simulations and Optimal Control."
                linkText="Take and Understand Action"
              />
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}

function FeatureCard({ icon, title, description, linkText }) {
  return (
    <div className="flex flex-col items-center gap-4 text-center group">
      <div className="transition-transform duration-300 group-hover:scale-110">
        {icon}
      </div>
      <div>
        <h3 className="text-lg font-medium text-black group-hover:text-black/90 transition-colors duration-300">
          {title}
        </h3>
        <p className="text-black/80 group-hover:text-black/70 transition-colors duration-300">
          {description}
        </p>
        <Link
          href="#"
          className="text-black/60 hover:text-black/90 transition-colors duration-300"
          prefetch={false}
        >
          {linkText}
        </Link>
      </div>
    </div>
  );
}

// ... (The icon components remain the same)

function ExploreIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
    </svg>
  );
}

function SatelliteIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-12 w-12 text-primary-foreground"
    >
      <path d="M13 7 9 3 5 7l4 4" />
      <path d="m17 11 4 4-4 4-4-4" />
      <path d="m8 12 4 4 6-6-4-4Z" />
      <path d="m16 8 3-3" />
      <path d="M9 21a6 6 0 0 0-6-6" />
    </svg>
  );
}

function AssimilatorIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-12 w-12 text-primary-foreground"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20" />
      <path d="M12 2v20" />
      <path d="m4.93 4.93 14.14 14.14" />
      <path d="m19.07 4.93-14.14 14.14" />
    </svg>
  );
}

function CloudSunRainIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-12 w-12 text-primary-foreground"
    >
      <path d="M12 2v2" />
      <path d="m4.93 4.93 1.41 1.41" />
      <path d="M20 12h2" />
      <path d="m19.07 4.93-1.41 1.41" />
      <path d="M15.947 12.65a4 4 0 0 0-5.925-4.128" />
      <path d="M3 20a5 5 0 1 1 8.9-4H13a3 3 0 0 1 2 5.24" />
      <path d="M11 20v2" />
      <path d="M7 19v2" />
    </svg>
  );
}

function EnsembleIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-12 w-12 text-primary-foreground"
    >
      <circle cx="12" cy="12" r="2" />
      <path d="M12 2v4" />
      <path d="M12 18v4" />
      <path d="M4.93 4.93l2.83 2.83" />
      <path d="M16.24 16.24l2.83 2.83" />
      <path d="M2 12h4" />
      <path d="M18 12h4" />
      <path d="M4.93 19.07l2.83-2.83" />
      <path d="M16.24 7.76l2.83-2.83" />
    </svg>
  );
}

function VectorDatabaseIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-12 w-12 text-primary-foreground"
    >
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
    </svg>
  );
}

function RobotIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-12 w-12 text-primary-foreground"
    >
      <rect x="3" y="11" width="18" height="10" rx="2" />
      <circle cx="12" cy="5" r="2" />
      <path d="M12 7v4" />
      <line x1="8" y1="16" x2="8" y2="16" />
      <line x1="16" y1="16" x2="16" y2="16" />
      <path d="M19 2l2 2-2 2" />
    </svg>
  );
}
