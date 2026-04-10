import { PlanStep, KnowledgeEntry } from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE || 'http://20.40.60.199:8000';

export const api = {
  /**
   * Placeholder for streaming task execution from FastAPI
   */
  async *streamTask(goal: string) {
    // In a real app, this would use fetch with a ReadableStream or WebSockets
    // For now, we simulate the backend response steps
    
    const mockSteps: PlanStep[] = [
      {
        id: '1',
        title: 'Analyze Request Context',
        description: 'Evaluating the depth and scope of the user request.',
        status: 'completed',
        stage: 'explore',
        risk: { score: 10, level: 'low', reasoning: 'Standard context analysis.' },
        requiresApproval: false
      },
      {
        id: '2',
        title: 'Access External Knowledge Base',
        description: 'Retrieving relevant patterns from the knowledge ledger.',
        status: 'completed',
        stage: 'explore',
        risk: { score: 25, level: 'low', reasoning: 'Read-only access to internal data.' },
        requiresApproval: false
      },
      {
        id: '3',
        title: 'Execute System Modification',
        description: 'Applying changes to the core configuration files.',
        status: 'pending',
        stage: 'execute',
        risk: { score: 85, level: 'high', reasoning: 'High impact on system stability. Requires human verification.' },
        requiresApproval: true
      },
      {
        id: '4',
        title: 'Verify Integrity',
        description: 'Running validation suite to ensure compliance.',
        status: 'pending',
        stage: 'validate',
        risk: { score: 15, level: 'low', reasoning: 'Standard validation procedure.' },
        requiresApproval: false
      }
    ];

    for (const step of mockSteps) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      yield step;
    }
  },

  /**
   * Placeholder for polling governance status
   */
  async checkApprovalStatus(stepId: string): Promise<boolean> {
    try {
      const response = await fetch(`${BASE_URL}/governance/status/${stepId}`);
      if (!response.ok) return false;
      const data = await response.json();
      return data.approved;
    } catch (e) {
      console.warn('FastAPI backend not reachable at localhost:8000. Using mock approval.');
      return true; // Mock fallback
    }
  },

  /**
   * Placeholder for fetching knowledge ledger
   */
  async getKnowledgeLedger(): Promise<KnowledgeEntry[]> {
    return [
      {
        id: 'k1',
        category: 'pattern',
        content: 'Preferred deployment strategy: Blue-Green for high-availability services.',
        source: 'System Audit Q1',
        timestamp: '2026-04-01T10:00:00Z'
      },
      {
        id: 'k2',
        category: 'constraint',
        content: 'Maximum concurrent API calls limited to 50 per second for external endpoints.',
        source: 'Security Policy v2.1',
        timestamp: '2026-04-05T14:30:00Z'
      },
      {
        id: 'k3',
        category: 'fact',
        content: 'Last successful system-wide validation completed with 0 critical errors.',
        source: 'Validation Bot',
        timestamp: '2026-04-07T09:15:00Z'
      }
    ];
  }
};
