import React, { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import styles from "./ChatWithDocs.module.css";

const apiQuestions = {
  "Data Ingestion API": [
    "How can I use Constellation's Data Ingestion API to streamline my data pipeline?",
    "What data formats are supported by the Data Ingestion API?",
    "Can the Data Ingestion API handle real-time satellite data streams?",
  ],
  "Satellite Imagery Foundation Models API": [
    "What pre-trained models are available in the Satellite Imagery Foundation Models API?",
    "How can I fine-tune a model from the Satellite Imagery Foundation Models API for my specific use case?",
    "Can the Satellite Imagery Foundation Models API handle multi-spectral imagery?",
  ],
  "Climate / Weather Model Prediction API": [
    "How accurate are the climate predictions from the Climate / Weather Model Prediction API?",
    "Can I integrate my own data with the Climate / Weather Model Prediction API?",
    "What's the spatial and temporal resolution of the Climate / Weather Model Prediction API?",
  ],
  "Ensemble Toolkit API": [
    "How does the Ensemble Toolkit API improve prediction accuracy?",
    "Can I use the Ensemble Toolkit API with my own custom models?",
    "What visualization tools are available in the Ensemble Toolkit API?",
  ],
  "Reinforcement Learning API": [
    "How can I use the Reinforcement Learning API for environmental policy optimization?",
    "What environments are available in the Reinforcement Learning API?",
    "Can the Reinforcement Learning API handle multi-agent scenarios?",
  ],
};

const allQuestions = Object.values(apiQuestions).flat();

export function ChatWithDocs() {
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(true);
  const [selectedAPI, setSelectedAPI] = useState<string | null>(null);
  const [questions, setQuestions] = useState(allQuestions);
  const [isHovering, setIsHovering] = useState(false);
  const [isUserTyping, setIsUserTyping] = useState(false);
  const [llmResponse, setLlmResponse] = useState("");
  const [showDialog, setShowDialog] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let timer;
    if (isTyping && !isUserTyping) {
      if (currentQuestion.length < questions[questionIndex].length) {
        timer = setTimeout(() => {
          setCurrentQuestion(
            questions[questionIndex].slice(0, currentQuestion.length + 1),
          );
        }, 50);
      } else {
        setIsTyping(false);
        timer = setTimeout(() => {
          setIsTyping(true);
          setCurrentQuestion("");
        }, 3000);
      }
    } else if (!isTyping && !isUserTyping) {
      if (currentQuestion.length > 0) {
        timer = setTimeout(() => {
          setCurrentQuestion(currentQuestion.slice(0, -1));
        }, 30);
      } else {
        timer = setTimeout(() => {
          setIsTyping(true);
          setQuestionIndex((prevIndex) => (prevIndex + 1) % questions.length);
        }, 1000);
      }
    }
    return () => clearTimeout(timer);
  }, [currentQuestion, isTyping, questionIndex, questions, isUserTyping]);

  const handleAPISelect = (api: string | null) => {
    setSelectedAPI(api);
    setQuestions(api ? apiQuestions[api] : allQuestions);
    setQuestionIndex(0);
    setCurrentQuestion("");
    setIsTyping(true);
    setIsUserTyping(false);
    setShowDialog(false);
    setError(null);
  };

  const handleInputClick = () => {
    setIsUserTyping(true);
    setIsTyping(false);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentQuestion(e.target.value);
  };

  const handleInputBlur = () => {
    if (currentQuestion.trim() === "") {
      setIsUserTyping(false);
      setIsTyping(true);
      setCurrentQuestion("");
    }
  };

  const renderFormattedText = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return <span key={index}>{part}</span>;
    });
  };
  const [dialogVisible, setDialogVisible] = useState(false);
  const [typingStarted, setTypingStarted] = useState(false);

  const handleKeyPress = async (e: React.KeyboardEvent<HTMLInputElement>) => {};

  return (
    <div className="flex flex-col items-center gap-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
          It's never been easier to get started
        </h1>
        <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
          Chat with our docs using our complimentary LLM to streamline your
          implementation of Constellation
        </p>
      </div>
      <div className="flex items-center gap-4 w-full max-w-4xl justify-between">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="w-64">
              {selectedAPI || "Select Earth Science API"}
              <ChevronDownIcon className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-64">
            <DropdownMenuItem onSelect={() => handleAPISelect(null)}>
              All APIs
            </DropdownMenuItem>
            {Object.keys(apiQuestions).map((api) => (
              <DropdownMenuItem key={api} onSelect={() => handleAPISelect(api)}>
                {api}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>Powered by </span>
          <Image
            src="/Claude Ai.svg"
            alt="Claude AI Logo"
            width={70}
            height={70}
          />
        </div>
      </div>
      <div
        className={`relative w-full max-w-4xl ${styles.inputContainer} transition-all duration-300 ease-in-out transform hover:scale-[1.02] hover:shadow-xl`}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
          <BotIcon className="w-8 h-8 text-muted-foreground" />
        </div>
        <Input
          ref={inputRef}
          type="text"
          value={currentQuestion}
          onChange={handleInputChange}
          onClick={handleInputClick}
          onBlur={handleInputBlur}
          onKeyPress={handleKeyPress}
          readOnly={!isUserTyping || isLoading}
          className="pl-16 pr-4 py-8 rounded-full bg-background border border-input focus:border-primary focus:ring-primary text-xl shadow-lg transition-all duration-300 ease-in-out"
          placeholder={
            isLoading
              ? "Generating workflow..."
              : "Ask about Earth Observation workflows..."
          }
        />
      </div>
      {showDialog && (
        <div
          className={`w-full max-w-4xl mt-4 p-8 rounded-2xl shadow-2xl bg-gradient-to-br from-white to-gray-50 backdrop-blur-sm border border-gray-200 backdrop-filter backdrop-blur-lg bg-opacity-80 transition-opacity duration-1000 ease-in-out ${
            dialogVisible ? "opacity-100" : "opacity-0"
          }`}
        >
          <h3 className="font-bold mb-4 text-2xl text-primary">
            Generated Earth Observation Workflow:
          </h3>
          {isLoading ? (
            <p className="text-muted-foreground">Generating workflow...</p>
          ) : error ? (
            <p className="text-red-500">{error}</p>
          ) : (
            <div className="prose prose-sm max-w-none">
              {typingStarted ? renderFormattedText(llmResponse) : null}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function BotIcon(props) {
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
      <path d="M12 8V4H8" />
      <rect width="16" height="12" x="4" y="8" rx="2" />
      <path d="M2 14h2" />
      <path d="M20 14h2" />
      <path d="M15 13v2" />
      <path d="M9 13v2" />
    </svg>
  );
}

function ChevronDownIcon(props) {
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
      <path d="m6 9 6 6 6-6" />
    </svg>
  );
}
