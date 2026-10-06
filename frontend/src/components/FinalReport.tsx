import React from 'react';
import { Download, Check, ExternalLink, ShieldCheck } from 'lucide-react';

export default function FinalReport() {
  return (
    <div className="h-full bg-gray-950 p-6 overflow-auto">
      <div className="max-w-4xl mx-auto space-y-8 pb-12">
        
        {/* Header */}
        <div className="border-b border-gray-800 pb-6 flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-100 mb-2">Autonomous Repair Report</h1>
            <div className="text-sm text-gray-400 font-mono">
              Task ID: tk_8f92a1b4 • Generated: {new Date().toLocaleString()}
            </div>
          </div>
          <div className="flex gap-2">
            <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-200 text-sm rounded-md transition-colors border border-gray-700">
              <Download className="w-4 h-4" /> Export PDF
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-md transition-colors shadow-[0_0_15px_rgba(37,99,235,0.4)]">
              <GitMerge className="w-4 h-4" /> Create PR
            </button>
          </div>
        </div>

        {/* Executive Summary */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-200 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-green-500" /> Executive Summary
          </h2>
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-5 text-gray-300 text-sm leading-relaxed">
            <p className="mb-3">
              RepoGuard AI successfully diagnosed and resolved a high-severity race condition in the <code className="bg-gray-800 text-blue-300 px-1 rounded">SessionManager</code> component. 
            </p>
            <p>
              The issue occurred during concurrent session creation when the system approached the maximum session limit, leading to map size violations and potential memory leaks. A Mutex locking mechanism was introduced to ensure atomic check-then-act operations. The fix was verified against existing regression suites and a newly synthesized high-concurrency load test.
            </p>
          </div>
        </section>

        {/* Changes Summary */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-200">Files Modified</h2>
          <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-800/50 text-gray-400 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3 font-medium">File</th>
                  <th className="px-4 py-3 font-medium">Action</th>
                  <th className="px-4 py-3 font-medium">Stats</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                <tr className="hover:bg-gray-800/50">
                  <td className="px-4 py-3 font-mono text-gray-300 flex items-center gap-2">
                    <ExternalLink className="w-3 h-3 text-gray-500" /> src/auth/SessionManager.ts
                  </td>
                  <td className="px-4 py-3 text-yellow-400">Modified</td>
                  <td className="px-4 py-3 font-mono text-xs">
                    <span className="text-green-400">+6</span> <span className="text-red-400">-4</span>
                  </td>
                </tr>
                <tr className="hover:bg-gray-800/50">
                  <td className="px-4 py-3 font-mono text-gray-300 flex items-center gap-2">
                    <ExternalLink className="w-3 h-3 text-gray-500" /> package.json
                  </td>
                  <td className="px-4 py-3 text-yellow-400">Modified</td>
                  <td className="px-4 py-3 font-mono text-xs">
                    <span className="text-green-400">+1</span> <span className="text-red-400">-0</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Verification */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-200">Verification & Safety</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <h3 className="font-medium text-gray-300 mb-3 text-sm">Testing Pipeline</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-500" /> Synthesized test generated
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-500" /> Synthesized test passed (500 ops/s)
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-500" /> Baseline regression tests passed
                </li>
              </ul>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <h3 className="font-medium text-gray-300 mb-3 text-sm">Static Analysis</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-500" /> Type checking passed
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-500" /> Linting rules satisfied
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-500" /> No indirect impact violations
                </li>
              </ul>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}

// Simple local mock for GitMerge icon if not available from lucide
const GitMerge = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <circle cx="18" cy="18" r="3"></circle>
    <circle cx="6" cy="6" r="3"></circle>
    <path d="M6 21V9a9 9 0 0 0 9 9"></path>
  </svg>
);
