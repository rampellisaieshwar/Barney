import { PlanStep, KnowledgeEntry } from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE || '/api';

export const api = {
  /**
   * Placeholder for streaming task execution from FastAPI
   */
  async *streamTask(goal: string) {
    const BASE = import.meta.env.VITE_API_BASE || '/api';
    const API_KEY = import.meta.env.VITE_API_KEY || 'your-secret';

    try {
      // Submit task
      const startRes = await fetch(`${BASE}/run_task`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': API_KEY
        },
        body: JSON.stringify({ task: goal, user_id: "test_user" })
      });
      if (!startRes.ok) throw new Error("Failed to start task");
      const { task_id } = await startRes.json();

      // Poll until done
      let isDone = false;
      let lastLogsCount = 0;

      while (!isDone) {
        await new Promise(r => setTimeout(r, 2000));

        const statusRes = await fetch(`${BASE}/status/${task_id}`, {
          headers: { 'x-api-key': API_KEY }
        });
        if (!statusRes.ok) continue;

        const data = await statusRes.json();
        const logs: string[] = data.logs || [];

        for (let i = lastLogsCount; i < logs.length; i++) {
          const raw = logs[i];
          let title = raw.substring(0, 60);
          let stage: 'explore' | 'execute' | 'validate' = 'explore';

          if (raw.includes('Detected:')) { title = '🤖 ' + raw.split('Detected:')[1]?.trim().substring(0, 50); }
          else if (raw.includes('Found') && raw.includes('key')) { title = '🔑 API key found in vault'; }
          else if (raw.includes('Generating Python code')) { title = '🧠 Generating Python code...'; stage = 'execute'; }
          else if (raw.includes('Code generated')) { title = '✅ Code generated'; stage = 'execute'; }
          else if (raw.includes('Installing package')) { title = '📦 Installing ' + (raw.split('Installing package:')[1]?.trim() || ''); stage = 'execute'; }
          else if (raw.includes('Running code')) { title = '🚀 Running code...'; stage = 'execute'; }
          else if (raw.includes('Result received')) { title = '✅ Got result from API'; stage = 'validate'; }
          else if (raw.includes('SIMPLE MODE')) { title = '⚡ Quick answer mode'; }
          else if (raw.includes('DEEP MODE')) { title = '🔍 Deep research mode'; }
          else if (raw.includes('Search:') || raw.includes('DDG') || raw.includes('Brave')) { title = '🔍 Searching the web...'; stage = 'execute'; }
          else if (raw.includes('Planner') || raw.includes('plan')) { title = '📋 Planning approach...'; }

          yield {
            id: `${task_id}-log-${i}`,
            title,
            description: raw,
            status: 'completed' as const,
            stage,
            risk: { score: 0, level: 'low' as const, reasoning: 'Process step' },
            requiresApproval: false
          };
        }
        lastLogsCount = logs.length;

        if (data.status === 'DONE' || data.status === 'FAILED') {
          isDone = true;
          const answer = typeof data.answer === 'string' && data.answer
            ? data.answer
            : data.result?.answer || '';

          if (answer) {
            yield {
              id: `${task_id}-answer`,
              title: 'Final Answer',
              description: answer,
              status: 'completed' as const,
              stage: 'validate' as const,
              risk: { score: 0, level: 'low' as const, reasoning: `Confidence: ${data.confidence}` },
              requiresApproval: false
            };
          }
        }
      }
    } catch (err) {
      console.error(err);
      yield {
        id: 'err',
        title: 'Connection Failed',
        description: 'Could not reach backend',
        status: 'failed' as const,
        stage: 'validate' as const,
        risk: { score: 100, level: 'high' as const, reasoning: 'Down' },
        requiresApproval: false
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
  },

  async getAgentModeStatus(): Promise<{ agent_mode: string }> {
    const res = await fetch(`${BASE_URL}/agent_mode/status?user_id=default`, {
      headers: { 'x-api-key': import.meta.env.VITE_API_KEY || 'your-secret' }
    });
    if (!res.ok) throw new Error("Failed to fetch agent mode status");
    return res.json();
  },

  async toggleAgentMode(enabled: boolean): Promise<{ status: string; agent_mode: string }> {
    const res = await fetch(`${BASE_URL}/agent_mode/toggle`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'x-api-key': import.meta.env.VITE_API_KEY || 'your-secret'
      },
      body: JSON.stringify({ user_id: "default", enabled })
    });
    if (!res.ok) throw new Error("Failed to toggle agent mode");
    return res.json();
  }
};
