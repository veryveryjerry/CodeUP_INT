export interface RepositoryInfo {
  id: string;
  url: string;
  name: string;
  description?: string;
  language?: string;
  framework?: string;
  fileCount: number;
}

export interface FileInfo {
  path: string;
  content?: string;
  size: number;
}

export interface SymbolInfo {
  name: string;
  type: string;
  filePath: string;
  lineStart: number;
  lineEnd: number;
}

export enum TaskState {
  PENDING = 'PENDING',
  RUNNING = 'RUNNING',
  SUCCESS = 'SUCCESS',
  FAILED = 'FAILED'
}

export interface TaskCreate {
  repoId: string;
  request: string;
}

export interface TaskStatus {
  taskId: string;
  state: TaskState;
  currentStep: number;
  totalSteps: number;
  message: string;
  error?: string;
}

export interface TaskResult {
  taskId: string;
  success: boolean;
  finalReport?: FinalReport;
}

export interface IssueAnalysis {
  summary: string;
  severity: string;
  affectedComponents: string[];
}

export interface RootCauseAnalysis {
  cause: string;
  evidence: string[];
}

export interface CodeEdit {
  filePath: string;
  original: string;
  replacement: string;
  startLine: number;
  endLine: number;
}

export interface PatchPlan {
  description: string;
  edits: CodeEdit[];
}

export interface PatchResult {
  success: boolean;
  diff: string;
}

export interface TestDetail {
  name: string;
  status: 'pass' | 'fail' | 'skip';
  duration: number;
  error?: string;
}

export interface TestResult {
  suiteName: string;
  passed: number;
  failed: number;
  details: TestDetail[];
}

export interface RegressionResult {
  baseline: TestResult;
  patched: TestResult;
  verdict: 'pass' | 'fail';
  newFailures: TestDetail[];
}

export enum EvidenceType {
  CODE_REFERENCE = 'CODE_REFERENCE',
  LOG_OUTPUT = 'LOG_OUTPUT',
  TEST_RESULT = 'TEST_RESULT',
  DOCUMENTATION = 'DOCUMENTATION'
}

export interface EvidenceRecord {
  id: string;
  claim: string;
  filePath?: string;
  symbol?: string;
  lines?: number[];
  reason: string;
  type: EvidenceType;
}

export interface ImpactRadius {
  directFiles: string[];
  indirectFiles: string[];
  criticalPaths: string[];
}

export enum PatchConfidenceLevel {
  HIGH = 'HIGH',
  MODERATE = 'MODERATE',
  LOW = 'LOW',
  REJECTED = 'REJECTED'
}

export interface ConfidenceScore {
  score: number;
  level: PatchConfidenceLevel;
  breakdown: {
    testCoverage: number;
    staticAnalysis: number;
    historicalReliability: number;
  };
}

export interface FinalReport {
  summary: string;
  issueAnalysis: IssueAnalysis;
  rootCause: RootCauseAnalysis;
  patchPlan: PatchPlan;
  testResults: RegressionResult;
  impact: ImpactRadius;
  confidence: ConfidenceScore;
}

export interface AgentEvent {
  id: string;
  taskId: string;
  timestamp: string;
  type: string;
  stepName: string;
  stepNumber: number;
  status: 'pending' | 'running' | 'success' | 'failed';
  message: string;
  details?: any;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  impactLevel?: 'direct' | 'indirect' | 'safe';
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
}

export interface DependencyGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
