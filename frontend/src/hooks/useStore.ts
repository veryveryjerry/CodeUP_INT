import { create } from 'zustand';
import { RepositoryInfo, TaskStatus, AgentEvent } from '../types';

interface AppState {
  currentRepo: RepositoryInfo | null;
  setCurrentRepo: (repo: RepositoryInfo | null) => void;
  
  currentTaskId: string | null;
  setCurrentTaskId: (id: string | null) => void;
  
  taskStatus: TaskStatus | null;
  setTaskStatus: (status: TaskStatus | null) => void;
  
  events: AgentEvent[];
  setEvents: (events: AgentEvent[]) => void;
  addEvent: (event: AgentEvent) => void;
}

export const useStore = create<AppState>((set) => ({
  currentRepo: null,
  setCurrentRepo: (repo) => set({ currentRepo: repo }),
  
  currentTaskId: null,
  setCurrentTaskId: (id) => set({ currentTaskId: id }),
  
  taskStatus: null,
  setTaskStatus: (status) => set({ taskStatus: status }),
  
  events: [],
  setEvents: (events) => set({ events }),
  addEvent: (event) => set((state) => ({ events: [...state.events, event] })),
}));
