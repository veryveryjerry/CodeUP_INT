import React from 'react';
import { Terminal, Shield, Check, X, ShieldAlert } from 'lucide-react';

const mockTests = [
  { name: 'auth/login.test.ts', status: 'pass', time: '124ms' },
  { name: 'auth/session.test.ts', status: 'pass', time: '89ms' },
  { name: 'auth/session.concurrency.test.ts', status: 'pass', time: '450ms', isNew: true },
  { name: 'user/profile.test.ts', status: 'pass', time: '210ms' },
  { name: 'api/middleware.test.ts', status: 'pass', time: '156ms' },
];

export default function TestConsole() {
  return (
    <div className="panel h-full flex flex-row">
      <div className="w-1/3 border-r border-gray-800 flex flex-col bg-gray-900">
        <div className="panel-header !bg-gray-900">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-green-500" />
            <span>Regression Shield</span>
          </div>
          <div className="text-xs bg-green-900/30 text-green-400 px-2 py-0.5 rounded border border-green-800/50">
            PASSED
          </div>
        </div>
        
        <div className="p-4 flex-1 overflow-auto">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-950 p-3 rounded border border-gray-800 text-center">
              <div className="text-2xl font-bold text-green-400">42</div>
              <div className="text-xs text-gray-500 uppercase">Baseline Tests</div>
            </div>
            <div className="bg-gray-950 p-3 rounded border border-gray-800 text-center">
              <div className="text-2xl font-bold text-blue-400">+1</div>
              <div className="text-xs text-gray-500 uppercase">Synthesized</div>
            </div>
          </div>
          
          <div className="space-y-1">
            {mockTests.map((test, idx) => (
              <div key={idx} className={`flex items-center justify-between p-2 rounded text-sm ${test.isNew ? 'bg-blue-900/10 border border-blue-900/30' : 'hover:bg-gray-800'}`}>
                <div className="flex items-center gap-2 overflow-hidden">
                  {test.status === 'pass' ? (
                    <Check className="w-3 h-3 text-green-500 shrink-0" />
                  ) : (
                    <X className="w-3 h-3 text-red-500 shrink-0" />
                  )}
                  <span className="font-mono text-xs truncate text-gray-300">{test.name}</span>
                  {test.isNew && (
                    <span className="text-[9px] bg-blue-900 text-blue-300 px-1 py-0.5 rounded uppercase font-bold shrink-0">Generated</span>
                  )}
                </div>
                <span className="text-xs text-gray-600 font-mono shrink-0">{test.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="flex-1 flex flex-col bg-[#0d1117]">
        <div className="px-4 py-2 border-b border-gray-800 bg-[#161b22] text-xs font-mono text-gray-400 flex items-center gap-2">
          <Terminal className="w-3 h-3" />
          Test Execution Output
        </div>
        <div className="p-4 font-mono text-xs overflow-auto flex-1 text-gray-300 leading-relaxed whitespace-pre">
          <span className="text-blue-400">repo-guard-ai@1.0.0</span> <span className="text-gray-500">test:regression</span><br/>
          $ vitest run --coverage<br/><br/>
          <span className="text-green-400">✓</span> src/auth/login.test.ts (4 tests) <span className="text-gray-500">124ms</span><br/>
          <span className="text-green-400">✓</span> src/auth/session.test.ts (8 tests) <span className="text-gray-500">89ms</span><br/>
          <span className="text-green-400">✓</span> src/user/profile.test.ts (12 tests) <span className="text-gray-500">210ms</span><br/>
          <span className="text-green-400">✓</span> src/api/middleware.test.ts (5 tests) <span className="text-gray-500">156ms</span><br/>
          <br/>
          <span className="text-yellow-400">▶</span> <span className="text-gray-400">Running synthesized test suite for autonomous patch...</span><br/>
          <span className="text-green-400">✓</span> src/auth/session.concurrency.test.ts (1 test) <span className="text-gray-500">450ms</span><br/>
          <span className="text-gray-500">  ↳ should handle 500 concurrent session creations without exceeding maxSessions</span><br/>
          <br/>
          <span className="text-green-400 font-bold">Test Suites: 5 passed, 5 total</span><br/>
          <span className="text-green-400 font-bold">Tests:       30 passed, 30 total</span><br/>
          <span className="text-gray-400">Snapshots:   0 total</span><br/>
          <span className="text-gray-400">Time:        1.029s</span><br/>
          <br/>
          <span className="text-blue-400 font-bold">REGRESSION SHIELD: VERIFIED</span><br/>
          <span className="text-gray-400">No regressions detected. Synthesized test passed. Fix is robust.</span>
        </div>
      </div>
    </div>
  );
}
