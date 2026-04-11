import { PlanStep, KnowledgeEntry } from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE || '/api';

export const api = {
  /**
   * Placeholder for streaming task execution from FastAPI
   */
  async *streamTask(goal: string) {
    try {
      // 1. Kick off the task
      const startRes = await fetch(`${BASE_URL}/run_task`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-api-key': import.meta.env.VITE_API_KEY || 'your-secret'
        },
        body: JSON.stringify({ task: goal, user_id: "test_user" })
      });
      if (!startRes.ok) throw new Error("Failed to start task");
      
      const { task_id } = await startRes.json();
      
      let isDone = false;
      let lastLogsCount = 0;
      
      while (!isDone) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2s
        
        const statusRes = await fetch(`${BASE_URL}/status/${task_id}`);
        if (!statusRes.ok) continue;
        
        const data = await statusRes.json();
        const logs = data.logs || [];
        
        // Yield new steps based on logs
        for (let i = lastLogsCount; i < logs.length; i++) {
          yield {
            id: `${task_id}-log-${i}`,
            title: logs[i].substring(0, 50),
            description: logs[i],
            status: 'completed',
            stage: logs[i].includes('TOOL') ? 'execute' : 'explore',
            risk: { score: 0, level: 'low', reasoning: 'Info log' },
            requiresApproval: false
          };
        }
        lastLogsCount = logs.length;
        
        if (data.status === 'DONE' || data.status === 'FAILED') {
           isDone = true;
           
           // PIPELINE CONTRACT: Extract answer with defensive fallbacks
           // Priority: data.answer (new flat) > data.result.answer (legacy nested) > data.result (raw string)
           let answer: string | null = null;
           
           if (typeof data.answer === 'string' && data.answer) {
             answer = data.answer;
           } else if (data.result && typeof data.result === 'object' && data.result.answer) {
             answer = typeof data.result.answer === 'string' 
               ? data.result.answer 
               : JSON.stringify(data.result.answer);
           } else if (typeof data.result === 'string' && data.result) {
             answer = data.result;
           }
           
           console.log("[BARNEY DEBUG] API Response:", JSON.stringify(data).substring(0, 500));
           console.log("[BARNEY DEBUG] Extracted answer:", answer?.substring(0, 200));
           
           const confidence = data.confidence ?? data.result?.confidence ?? 0;
           const responseTime = data.response_time_ms ?? data.result?.response_time_ms ?? 0;
           
           if (answer) {
             yield {
                id: `${task_id}-answer`,
                title: 'Final Answer',
                description: answer,
                status: 'completed',
                stage: 'validate',
                risk: { score: 0, level: 'low' as const, reasoning: `Confidence: ${confidence}, Time: ${responseTime}ms` },
                requiresApproval: false
             };
           }
        }
      }
    } catch (err) {
      console.error(err);
      yield {
        id: 'err', title: 'Connection Failed', description: 'Could not reach backend',
        status: 'failed', stage: 'validate', risk: { score: 100, level: 'high', reasoning: 'Down' }, requiresApproval: false
      };
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
