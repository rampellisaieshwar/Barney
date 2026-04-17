import type { TaskStatus, PlanStep, Message } from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'dev_key';

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY,
      ...options.headers,
    },
  });
}

export async function startTask(goal: string, userId: string = 'default'): Promise<string> {
  const res = await fetchWithAuth(`${BASE_URL}/run_task`, {
    method: 'POST',
    body: JSON.stringify({ task: goal, user_id: userId }),
  });
  const data = await res.json();
  return data.task_id;
}

export async function getTaskStatus(taskId: string): Promise<TaskStatus> {
  const res = await fetchWithAuth(`${BASE_URL}/status/${taskId}`);
  return res.json();
}

export async function* streamTask(userMsg: string): AsyncGenerator<PlanStep, void, unknown> {
  const taskId = await startTask(userMsg);

  while (true) {
    await new Promise((r) => setTimeout(r, 1500));
    const status = await getTaskStatus(taskId);

    for (const log of status.logs) {
      yield log;
    }

    if (status.status === 'completed' || status.status === 'failed') {
      break;
    }
  }
}

export async function sendMessage(
  messages: Message[],
  onChunk: (step: PlanStep, isNew: boolean) => void
): Promise<void> {
  const userMsg = messages[messages.length - 1]?.content || '';

  for await (const step of streamTask(userMsg)) {
    onChunk(step, true);
  }
}

export function createMessage(content: string, role: 'user' | 'assistant'): Message {
  return {
    id: crypto.randomUUID(),
    content,
    role,
    timestamp: new Date(),
  };
}