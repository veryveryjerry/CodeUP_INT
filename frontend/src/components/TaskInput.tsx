import React, { useState } from 'react';
import { Terminal, Zap, Play } from 'lucide-react';
import { useStore } from '../hooks/useStore';
import { api } from '../services/api';

export default function TaskInput() {
  const [request, setRequest] = useState('');
  const [running, setRunning] = useState(false);
  const { currentRepo, setCurrentTaskId } = useStore();

  const handleRun = async () => {
    if (!currentRepo || !request) return;
    
    setRunning(true);
    try {
      const { taskId } = await api.createTask(currentRepo.id, request);
      setCurrentTaskId(taskId);
      await api.runTask(taskId);
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="panel h-full">
      <div className="panel-header bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-green-400" />
          <span>Task Request</span>
        </div>
      </div>
      
      <div className="p-3 flex flex-col h-full bg-gray-950">
        <textarea 
          className="flex-1 w-full bg-gray-900 border border-gray-700 rounded-md p-3 text-sm text-gray-200 focus:outline-none focus:border-blue-500 resize-none font-mono placeholder:font-sans"
          placeholder="Describe the issue or feature request (e.g., 'Fix the race condition in the user authentication service')"
          value={request}
          onChange={(e) => setRequest(e.target.value)}
          disabled={!currentRepo || running}
        />
        
        <div className="mt-3 flex justify-between items-center">
          <div className="text-xs text-gray-500 flex items-center gap-1">
            {currentRepo ? (
              <><span className="w-2 h-2 rounded-full bg-green-500"></span> Ready</>
            ) : (
              <><span className="w-2 h-2 rounded-full bg-red-500"></span> Repo required</>
            )}
          </div>
          
          <button 
            onClick={handleRun}
            disabled={!currentRepo || !request || running}
            className={`
              flex items-center gap-2 px-6 py-2 rounded-md font-bold text-sm transition-all
              ${(!currentRepo || !request || running) 
                ? 'bg-gray-800 text-gray-500 cursor-not-allowed' 
                : 'bg-blue-600 text-white hover:bg-blue-500 btn-run-autonomous'}
            `}
          >
            {running ? (
              <><Zap className="w-4 h-4 animate-pulse text-yellow-400" /> EXECUTING...</>
            ) : (
              <><Play className="w-4 h-4 fill-current" /> RUN AUTONOMOUS REPAIR</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
