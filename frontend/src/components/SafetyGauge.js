"use client";
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function SafetyGauge({ score = 0, size = 200 }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    // Simple counter animation
    const duration = 1000;
    const steps = 60;
    const stepTime = Math.abs(Math.floor(duration / steps));
    let current = 0;
    
    const timer = setInterval(() => {
      current += score / steps;
      if (current >= score) {
        setAnimatedScore(score);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.round(current));
      }
    }, stepTime);
    
    return () => clearInterval(timer);
  }, [score]);

  const strokeWidth = size * 0.1;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  let color = "#10B981"; // green
  if (score <= 40) color = "#F43F5E"; // red
  else if (score <= 70) color = "#FBBF24"; // yellow

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <motion.circle
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeLinecap="round"
          style={{ dropShadow: `0 0 10px ${color}` }}
        />
      </svg>
      
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold text-white drop-shadow-md">
          {animatedScore}
        </span>
        <span className="text-xs text-slate-400 font-medium tracking-wider mt-1">
          SAFETY SCORE
        </span>
      </div>
    </div>
  );
}
