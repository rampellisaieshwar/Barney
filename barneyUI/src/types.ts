export type View = 'console' | 'registry' | 'settings' | 'memory' | 'templates' | 'documents' | 'community' | 'help' | 'governance';

export interface Agent {
  id: string;
  name: string;
  description: string;
  successRate: number;
  toolsUsed: string[];
  icon: string;
}

export interface RiskAssessment {
  score: number; // 0-100
  level: 'low' | 'medium' | 'high' | 'critical';
  reasoning: string;
}

export interface PlanStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'blocked' | 'rejected';
  stage: 'explore' | 'execute' | 'validate';
  risk?: RiskAssessment;
  requiresApproval: boolean;
  approved?: boolean;
}

export interface TaskTrace {
  timestamp: string;
  type: 'thought' | 'tool' | 'result' | 'governance';
  content: string;
  metadata?: any;
}

export interface Insight {
  id: string;
  title: string;
  snippet: string;
  timestamp: string;
  tags?: string[];
}

export interface KnowledgeEntry {
  id: string;
  category: 'pattern' | 'constraint' | 'fact';
  content: string;
  source: string;
  timestamp: string;
}
