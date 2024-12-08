import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function PipelineDescription({
  children,
}: {
  children: React.ReactNode;
}) {
  const steps = [
    {
      name: "Drag",
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          className="w-6 h-6"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11"
          />
        </svg>
      ),
    },
    {
      name: "Drop",
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          className="w-6 h-6"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 14l-7 7m0 0l-7-7m7 7V3"
          />
        </svg>
      ),
    },
    {
      name: "Deploy",
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          className="w-6 h-6"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      ),
    },
  ];

  return (
    <Card className="flex-grow rounded-3xl overflow-hidden  group">
      <CardHeader className="text-center">
        <CardTitle className="text-3xl font-bold text-black">
          Data Pipeline Builder
        </CardTitle>
        <CardDescription className="text-lg text-black/80">
          Build and visualize your Earth Observation data pipelines with ease.
          <br />
          <span className="text-sm text-black/50">Powered by LLM-Composer</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="text-center">
        <>
          <div className="flex justify-center items-center mb-6">
            {steps.map((step, index) => (
              <React.Fragment key={step.name}>
                <div className="flex flex-col items-center">
                  <div className="bg-black rounded-full p-4 mb-2 flex items-center justify-center">
                    <div className="text-white mr-2">{step.icon}</div>
                    <span className="text-white font-semibold">
                      {step.name}
                    </span>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div className="w-16 border-t-2 border-dashed border-black/50 mx-2" />
                )}
              </React.Fragment>
            ))}
          </div>
          {children}
        </>
      </CardContent>
    </Card>
  );
}
