import React from 'react';
import { Activity, CheckCircle2, Circle, Clock, XCircle, Loader2 } from 'lucide-react';
import { useStore } from '../hooks/useStore';
import { useEventStream } from '../hooks/useEventStream';

const ALL_STEPS = [
  'Repository scanned',
  'Architecture reconstructed',
  'Issue understood',
  'Relevant symbols identified',
  'Impact radius calculated',
  'Patch strategy selected',
  'Files modified',
  'Regression test generated',
  'Tests executed',
  'Patch validated',
  'Confidence score calculated'
];

export default function ExecutionTimeline() {
  const { currentTaskId } = useStore();
  const { events } = useEventStream(currentTaskId);

  // Group events by step
  const getStepStatus = (stepName: string) => {
    const event = events.find(e => e.stepName === stepName);
    if (!event) return 'pending';
    return event.status;
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Circle className="w-5 h-5 text-gray-600" />;
    }
  };

  return (
    <div className="panel h-full">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-400" />
          <span>Agent Execution</span>
        </div>
        {currentTaskId && (
          <div className="text-xs bg-blue-900/30 text-blue-400 px-2 py-1 rounded border border-blue-800/50 flex items-center gap-1">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            Active
          </div>
        )}
      </div>
      
      <div className="panel-content bg-gray-950/50">
        {!currentTaskId ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500 p-6 text-center">
            <Clock className="w-10 h-10 mb-3 opacity-20" />
            <p className="text-sm">Waiting for task execution...</p>
          </div>
        ) : (
          <div className="relative pt-2 pb-6 px-4">
            {/* Timeline line */}
            <div className="absolute left-6 top-4 bottom-8 w-0.5 bg-gray-800 z-0"></div>
            
            <div className="space-y-6 relative z-10">
              {ALL_STEPS.map((step, index) => {
                const status = getStepStatus(step);
                const event = events.find(e => e.stepName === step);
                
                return (
                  <div key={index} className={`flex gap-3 ${status === 'pending' ? 'opacity-40' : 'opacity-100'} transition-opacity duration-500`}>
                    <div className="mt-0.5 bg-gray-950 rounded-full">
                      {getStepIcon(status)}
                    </div>
                    <div className="flex-1">
                      <div className={`font-medium text-sm ${status === 'running' ? 'text-blue-400' : (status === 'success' ? 'text-gray-200' : 'text-gray-400')}`}>
                        {index + 1}. {step}
                      </div>
                      {event && event.message && (
                        <div className="text-xs text-gray-500 mt-1 font-mono bg-gray-900 p-1.5 rounded border border-gray-800">
                          {event.message}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
