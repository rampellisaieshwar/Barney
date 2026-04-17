export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface PlanStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'blocked' | 'rejected';
  stage: 'explore' | 'execute' | 'validate';
  risk?: RiskAssessment;
  requiresApproval: boolean;
}

export interface RiskAssessment {
  score: number;
  level: 'low' | 'medium' | 'high' | 'critical';
  reasoning: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  logs: PlanStep[];
  error?: string;
}

export interface StreamingStep {
  step: PlanStep;
  isNew: boolean;
}