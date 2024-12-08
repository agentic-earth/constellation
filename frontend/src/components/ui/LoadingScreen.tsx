// File: src/components/ui/LoadingScreen.tsx

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

const loadingMessages = [
  "Cooking up your model...",
  "The stars are aligning...",
  "Crunching the numbers...",
  "Fetching data from the cosmos...",
  "Warming up the AI...",
  "Diving into the data ocean...",
  "Calibrating the crystal ball...",
  "Consulting with the digital oracles...",
  "Spinning up the quantum computer...",
  "Decoding the secrets of the universe...",
];

const LoadingScreen: React.FC = () => {
  const [message, setMessage] = useState("");

  useEffect(() => {
    const randomIndex = Math.floor(Math.random() * loadingMessages.length);
    setMessage(loadingMessages[randomIndex]);
  }, []);

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-gradient-to-br from-primary to-primary/90">
      <div className="text-center">
        <motion.div
          className="w-16 h-16 mb-8 mx-auto"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 360],
            borderRadius: ["20%", "50%", "20%"],
          }}
          transition={{
            duration: 2,
            ease: "easeInOut",
            times: [0, 0.5, 1],
            repeat: Infinity,
          }}
        >
          <div className="w-full h-full bg-primary-foreground opacity-75"></div>
        </motion.div>
        <motion.p
          className="text-xl text-primary-foreground"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {message}
        </motion.p>
      </div>
    </div>
  );
};

export default LoadingScreen;
