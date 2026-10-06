import React from 'react';

export default function ConfidenceScore({ score = 0 }: { score?: number }) {
  const getScoreColor = () => {
    if (score >= 90) return 'text-green-400';
    if (score >= 75) return 'text-yellow-400';
    if (score >= 50) return 'text-orange-400';
    return 'text-red-400';
  };

  const getStrokeColor = () => {
    if (score >= 90) return '#4ade80';
    if (score >= 75) return '#facc15';
    if (score >= 50) return '#fb923c';
    return '#f87171';
  };

  const getLabel = () => {
    if (score >= 90) return 'HIGH CONFIDENCE';
    if (score >= 75) return 'MODERATE CONFIDENCE';
    if (score >= 50) return 'LOW CONFIDENCE';
    return 'REJECTED';
  };

  // Circle math
  const radius = 24;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex items-center gap-4 bg-gray-950 p-2 rounded-lg border border-gray-800">
      <div className="relative w-16 h-16 flex items-center justify-center">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90 absolute" viewBox="0 0 64 64">
          <circle
            cx="32"
            cy="32"
            r={radius}
            className="stroke-gray-800"
            strokeWidth="6"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx="32"
            cy="32"
            r={radius}
            stroke={getStrokeColor()}
            strokeWidth="6"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
            strokeLinecap="round"
          />
        </svg>
        <div className={`text-xl font-bold ${getScoreColor()} z-10`}>
          {score}
        </div>
      </div>
      
      <div className="flex flex-col pr-2">
        <div className={`text-xs font-bold ${getScoreColor()}`}>
          {getLabel()}
        </div>
        <div className="text-[10px] text-gray-500 grid grid-cols-2 gap-x-3 gap-y-0.5 mt-1">
          <div className="flex justify-between">
            <span>Tests:</span> <span className="text-gray-300">100/100</span>
          </div>
          <div className="flex justify-between">
            <span>Static:</span> <span className="text-gray-300">95/100</span>
          </div>
          <div className="flex justify-between">
            <span>Impact:</span> <span className="text-gray-300">80/100</span>
          </div>
        </div>
      </div>
    </div>
  );
}
