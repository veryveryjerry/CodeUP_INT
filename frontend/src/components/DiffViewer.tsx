import React from 'react';
import { DiffEditor } from '@monaco-editor/react';
import { FileCode, GitCommit } from 'lucide-react';

const mockOriginalCode = `
export class SessionManager {
  private activeSessions: Map<string, Session> = new Map();
  private maxSessions = 100;

  public createSession(userId: string): Session {
    // BUG: Race condition when near max sessions
    if (this.activeSessions.size >= this.maxSessions) {
      this.evictOldestSession();
    }
    
    const session = new Session(userId);
    this.activeSessions.set(session.id, session);
    return session;
  }
  
  private evictOldestSession() {
    const oldestKey = this.activeSessions.keys().next().value;
    this.activeSessions.delete(oldestKey);
  }
}
`;

const mockModifiedCode = `
export class SessionManager {
  private activeSessions: Map<string, Session> = new Map();
  private maxSessions = 100;
  private readonly lock = new Mutex(); // Added mutex for thread safety

  public async createSession(userId: string): Promise<Session> {
    return await this.lock.runExclusive(() => {
      // FIX: Safe check and eviction under lock
      if (this.activeSessions.size >= this.maxSessions) {
        this.evictOldestSession();
      }
      
      const session = new Session(userId);
      this.activeSessions.set(session.id, session);
      return session;
    });
  }
  
  private evictOldestSession() {
    const oldestKey = this.activeSessions.keys().next().value;
    this.activeSessions.delete(oldestKey);
  }
}
`;

export default function DiffViewer() {
  return (
    <div className="h-full flex flex-col">
      <div className="bg-gray-900 border-b border-gray-800 p-2 flex gap-2 overflow-x-auto">
        <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 text-gray-200 text-sm rounded-md border border-gray-700 whitespace-nowrap">
          <FileCode className="w-4 h-4 text-blue-400" />
          src/auth/SessionManager.ts
          <span className="ml-2 text-xs bg-gray-700 px-1.5 py-0.5 rounded text-gray-300">1 edit</span>
        </button>
      </div>
      
      <div className="flex-1 bg-[#1e1e1e] relative">
        <DiffEditor
          height="100%"
          language="typescript"
          theme="vs-dark"
          original={mockOriginalCode}
          modified={mockModifiedCode}
          options={{
            readOnly: true,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 13,
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            renderSideBySide: true,
          }}
          className="react-monaco-editor-diff"
        />
        
        {/* Overlay for diff info */}
        <div className="absolute top-4 right-6 pointer-events-none z-10 flex gap-4">
          <div className="bg-red-900/40 text-red-300 px-3 py-1 rounded text-xs border border-red-800/50 flex items-center gap-1 backdrop-blur-sm">
            <span className="font-bold">-</span> 4 lines removed
          </div>
          <div className="bg-green-900/40 text-green-300 px-3 py-1 rounded text-xs border border-green-800/50 flex items-center gap-1 backdrop-blur-sm">
            <span className="font-bold">+</span> 6 lines added
          </div>
        </div>
      </div>
    </div>
  );
}
