import React from 'react';
import { Search, AlertTriangle, FileText, Code2, ListTree, Bug, Flame } from 'lucide-react';
import { EvidenceType } from '../types';

const mockEvidence = [
  {
    id: '1',
    claim: 'Race condition exists in session creation under high concurrency',
    type: EvidenceType.LOG_OUTPUT,
    reason: 'Production logs indicate Error: Map size exceeded 100 on multiple concurrent requests.',
    file: 'logs/production-error.log',
  },
  {
    id: '2',
    claim: 'Map operations are not thread-safe in the current execution context',
    type: EvidenceType.DOCUMENTATION,
    reason: 'Node.js event loop can be interrupted between size check and set operation if asynchronous operations intervene (though this specific code is synchronous, the surrounding context in production is not).',
  },
  {
    id: '3',
    claim: 'The issue is localized to the createSession method',
    type: EvidenceType.CODE_REFERENCE,
    reason: 'Method lacks locking mechanism for concurrent state mutations.',
    file: 'src/auth/SessionManager.ts',
    lines: [5, 12],
    symbol: 'createSession'
  },
  {
    id: '4',
    claim: 'Proposed fix resolves the race condition',
    type: EvidenceType.TEST_RESULT,
    reason: 'Synthesized load test with 500 concurrent requests completed successfully with 0 evict errors after applying the mutex pattern.',
  }
];

export default function EvidencePanel() {
  const getIcon = (type: EvidenceType) => {
    switch (type) {
      case EvidenceType.CODE_REFERENCE: return <Code2 className="w-4 h-4 text-blue-400" />;
      case EvidenceType.LOG_OUTPUT: return <AlertTriangle className="w-4 h-4 text-orange-400" />;
      case EvidenceType.TEST_RESULT: return <ListTree className="w-4 h-4 text-green-400" />;
      case EvidenceType.DOCUMENTATION: return <FileText className="w-4 h-4 text-purple-400" />;
    }
  };

  return (
    <div className="h-full flex flex-col p-4 bg-gray-950 overflow-auto">
      
      <div className="mb-6 grid grid-cols-2 gap-4 shrink-0">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Bug className="w-5 h-5 text-red-400" />
            <h3 className="font-semibold text-gray-200">Root Cause Identified</h3>
          </div>
          <p className="text-sm text-gray-400 leading-relaxed">
            The <code className="text-blue-300 bg-gray-800 px-1 rounded">SessionManager.createSession</code> method performs a check-then-act sequence on <code className="text-blue-300 bg-gray-800 px-1 rounded">activeSessions</code>. When called concurrently in the async environment, multiple requests pass the size check before any eviction occurs, causing the map to exceed its limit.
          </p>
        </div>
        
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Flame className="w-5 h-5 text-orange-400" />
            <h3 className="font-semibold text-gray-200">Fix Strategy</h3>
          </div>
          <p className="text-sm text-gray-400 leading-relaxed">
            Introduce a Mutex (mutual exclusion lock) around the critical section in <code className="text-blue-300 bg-gray-800 px-1 rounded">createSession</code>. This ensures that the check for max sessions and the subsequent insertion/eviction happen atomically per logical thread.
          </p>
        </div>
      </div>

      <div className="flex-1">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Supporting Evidence ({mockEvidence.length})</h3>
        <div className="space-y-3">
          {mockEvidence.map((evidence) => (
            <div key={evidence.id} className="bg-gray-900 border border-gray-800 rounded-lg p-3 hover:border-gray-700 transition-colors">
              <div className="flex items-start gap-3">
                <div className="mt-1 bg-gray-950 p-1.5 rounded-md border border-gray-800">
                  {getIcon(evidence.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm text-gray-200 mb-1">{evidence.claim}</div>
                  <div className="text-sm text-gray-400 mb-2">{evidence.reason}</div>
                  
                  {evidence.file && (
                    <div className="flex items-center gap-2 text-xs font-mono text-gray-500 bg-gray-950/50 p-1.5 rounded inline-flex border border-gray-800/50">
                      <span>{evidence.file}</span>
                      {evidence.lines && <span>:{evidence.lines[0]}-{evidence.lines[1]}</span>}
                      {evidence.symbol && <span className="text-blue-400 border-l border-gray-700 pl-2 ml-1">{evidence.symbol}</span>}
                    </div>
                  )}
                </div>
                <div className="text-[10px] uppercase font-bold text-gray-600 bg-gray-800 px-2 py-1 rounded">
                  {evidence.type.replace('_', ' ')}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
