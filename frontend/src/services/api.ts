import axios from 'axios';
import {
  RepositoryInfo,
  FileInfo,
  TaskCreate,
  TaskStatus,
  DependencyGraph,
  TestResult,
  EvidenceRecord,
  ImpactRadius
} from '../types';

const API_BASE = '/api';

export const api = {
  analyzeRepository: async (url: string): Promise<RepositoryInfo> => {
    // Mock implementation for UI development
    return {
      id: 'repo-' + Math.random().toString(36).substr(2, 9),
      url,
      name: url.split('/').pop() || 'unknown',
      language: 'TypeScript',
      framework: 'React',
      fileCount: 154
    };
    /*
    const res = await axios.post(`${API_BASE}/repos/analyze`, { url });
    return res.data;
    */
  },
  
  createTask: async (repoId: string, request: string): Promise<{ taskId: string }> => {
    // Mock
    return { taskId: 'task-' + Math.random().toString(36).substr(2, 9) };
    /*
    const res = await axios.post(`${API_BASE}/tasks`, { repoId, request });
    return res.data;
    */
  },
  
  runTask: async (taskId: string): Promise<void> => {
    // Mock
    return;
    /*
    await axios.post(`${API_BASE}/tasks/${taskId}/run`);
    */
  },
  
  getTask: async (taskId: string): Promise<TaskStatus> => {
    const res = await axios.get(`${API_BASE}/tasks/${taskId}`);
    return res.data;
  },
  
  getTaskDiff: async (taskId: string): Promise<string> => {
    const res = await axios.get(`${API_BASE}/tasks/${taskId}/diff`);
    return res.data.diff;
  },
  
  getTaskTests: async (taskId: string): Promise<TestResult[]> => {
    const res = await axios.get(`${API_BASE}/tasks/${taskId}/tests`);
    return res.data;
  },
  
  getTaskEvidence: async (taskId: string): Promise<EvidenceRecord[]> => {
    const res = await axios.get(`${API_BASE}/tasks/${taskId}/evidence`);
    return res.data;
  },
  
  getTaskImpact: async (taskId: string): Promise<ImpactRadius> => {
    const res = await axios.get(`${API_BASE}/tasks/${taskId}/impact`);
    return res.data;
  },
  
  getRepoGraph: async (repoId: string): Promise<DependencyGraph> => {
    const res = await axios.get(`${API_BASE}/repos/${repoId}/graph`);
    return res.data;
  },
  
  getRepoFiles: async (repoId: string): Promise<FileInfo[]> => {
    // Mock
    return [
      { path: 'src/App.tsx', size: 1024 },
      { path: 'src/utils/api.ts', size: 2048 },
      { path: 'src/components/Button.tsx', size: 512 }
    ];
    /*
    const res = await axios.get(`${API_BASE}/repos/${repoId}/files`);
    return res.data;
    */
  },
  
  healthCheck: async (): Promise<boolean> => {
    try {
      await axios.get(`${API_BASE}/health`);
      return true;
    } catch {
      return false;
    }
  }
};
