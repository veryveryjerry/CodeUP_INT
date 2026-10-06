import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import { Shield } from 'lucide-react';

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-gray-950 text-gray-100 font-sans">
        {/* Header */}
        <header className="h-14 border-b border-gray-800 bg-gray-900 flex items-center px-6 shrink-0 z-10 shadow-sm">
          <div className="flex items-center gap-2">
            <Shield className="w-6 h-6 text-blue-500" />
            <h1 className="text-xl font-bold tracking-wider text-gray-100">
              REPOGUARD <span className="text-blue-500">AI</span>
            </h1>
          </div>
          <div className="ml-auto flex items-center gap-4 text-sm text-gray-400">
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              System Online
            </div>
          </div>
        </header>
        
        {/* Main Content */}
        <main className="flex-1 overflow-hidden p-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
