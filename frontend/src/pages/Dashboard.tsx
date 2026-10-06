import React, { useState } from 'react';
import RepositoryPanel from '../components/RepositoryPanel';
import TaskInput from '../components/TaskInput';
import ExecutionTimeline from '../components/ExecutionTimeline';
import EvidencePanel from '../components/EvidencePanel';
import TestConsole from '../components/TestConsole';
import ImpactGraph from '../components/ImpactGraph';
import DiffViewer from '../components/DiffViewer';
import ConfidenceScore from '../components/ConfidenceScore';
import FinalReport from '../components/FinalReport';
import { useStore } from '../hooks/useStore';
import { Layout, GitMerge, FileCode, CheckCircle2 } from 'lucide-react';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'evidence' | 'impact' | 'diff' | 'report'>('evidence');
  const { currentTaskId } = useStore();

  return (
    <div className="h-full flex flex-col gap-4">
      {/* Top Half */}
      <div className="flex-1 flex gap-4 min-h-0">
        
        {/* Left Column: Repo & Input */}
        <div className="w-1/4 flex flex-col gap-4">
          <div className="flex-1 overflow-hidden">
            <RepositoryPanel />
          </div>
          <div className="h-64 shrink-0">
            <TaskInput />
          </div>
        </div>
        
        {/* Center Column: Execution Timeline */}
        <div className="w-1/4">
          <ExecutionTimeline />
        </div>
        
        {/* Right Column: Analysis Tabs */}
        <div className="flex-1 flex flex-col min-w-0 panel">
          <div className="panel-header !p-0">
            <div className="flex">
              <button 
                onClick={() => setActiveTab('evidence')}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'evidence' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'}`}
              >
                <div className="flex items-center gap-2"><Layout className="w-4 h-4" /> Evidence & Causes</div>
              </button>
              <button 
                onClick={() => setActiveTab('impact')}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'impact' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'}`}
              >
                <div className="flex items-center gap-2"><GitMerge className="w-4 h-4" /> Impact Radius</div>
              </button>
              <button 
                onClick={() => setActiveTab('diff')}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'diff' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'}`}
              >
                <div className="flex items-center gap-2"><FileCode className="w-4 h-4" /> Patch Diff</div>
              </button>
              <button 
                onClick={() => setActiveTab('report')}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'report' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'}`}
              >
                <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4" /> Final Report</div>
              </button>
            </div>
            
            {activeTab === 'report' && currentTaskId && (
              <div className="mr-4 scale-75 transform origin-right">
                <ConfidenceScore score={92} />
              </div>
            )}
          </div>
          
          <div className="panel-content !p-0 relative">
            {activeTab === 'evidence' && <EvidencePanel />}
            {activeTab === 'impact' && <ImpactGraph />}
            {activeTab === 'diff' && <DiffViewer />}
            {activeTab === 'report' && <FinalReport />}
          </div>
        </div>
      </div>
      
      {/* Bottom Half */}
      <div className="h-64 shrink-0">
        <TestConsole />
      </div>
    </div>
  );
}
