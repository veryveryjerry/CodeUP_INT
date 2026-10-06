import React, { useState } from 'react';
import { FolderGit2, Search, File, ChevronRight, ChevronDown, RefreshCw } from 'lucide-react';
import { useStore } from '../hooks/useStore';
import { api } from '../services/api';
import { FileInfo } from '../types';

export default function RepositoryPanel() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<FileInfo[]>([]);
  const { currentRepo, setCurrentRepo } = useStore();

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    
    setLoading(true);
    try {
      const repo = await api.analyzeRepository(url);
      setCurrentRepo(repo);
      const repoFiles = await api.getRepoFiles(repo.id);
      setFiles(repoFiles);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel h-full">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <FolderGit2 className="w-4 h-4" />
          <span>Repository Explorer</span>
        </div>
      </div>
      
      <div className="p-3 border-b border-gray-800 bg-gray-900">
        <form onSubmit={handleAnalyze} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input 
              type="text" 
              placeholder="GitHub Repository URL..." 
              className="w-full bg-gray-950 border border-gray-700 rounded-md py-1.5 pl-9 pr-3 text-sm text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
          <button 
            type="submit"
            disabled={loading || !url}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md text-sm font-medium transition-colors flex items-center justify-center min-w-[100px]"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Analyze'}
          </button>
        </form>
      </div>

      <div className="panel-content !p-0">
        {!currentRepo ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500 p-6 text-center">
            <FolderGit2 className="w-12 h-12 mb-3 opacity-20" />
            <p className="text-sm">Connect a repository to begin analysis and repair.</p>
          </div>
        ) : (
          <div className="flex flex-col h-full">
            <div className="px-4 py-3 bg-gray-800/30 border-b border-gray-800 flex justify-between items-center shrink-0">
              <div>
                <h3 className="font-medium text-sm text-gray-200">{currentRepo.name}</h3>
                <div className="text-xs text-gray-400 mt-0.5 flex gap-2">
                  <span>{currentRepo.language}</span>
                  <span>•</span>
                  <span>{currentRepo.framework}</span>
                </div>
              </div>
              <div className="text-xs px-2 py-1 bg-gray-800 rounded-md border border-gray-700">
                {currentRepo.fileCount} files
              </div>
            </div>
            
            <div className="flex-1 overflow-auto p-2">
              <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider px-2">Project Files</div>
              <div className="space-y-0.5">
                {files.map((file, idx) => (
                  <div key={idx} className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-800 rounded-md cursor-pointer text-sm text-gray-300 group">
                    <File className="w-4 h-4 text-gray-500 group-hover:text-blue-400" />
                    <span className="truncate">{file.path}</span>
                  </div>
                ))}
                {files.length === 0 && (
                  <div className="px-2 py-1 text-sm text-gray-500 italic">No files loaded</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
