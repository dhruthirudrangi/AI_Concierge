import type { FeedbackPayload } from '../types';

const STORAGE_KEY = 'cardconcierge_feedback';
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

function readFeedbackLog(): FeedbackPayload[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeFeedbackLog(entries: FeedbackPayload[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

export async function submitFeedback(payload: FeedbackPayload): Promise<void> {
  if (USE_MOCK || !API_BASE) {
    await new Promise((r) => setTimeout(r, 200));
    const log = readFeedbackLog();
    log.push(payload);
    writeFeedbackLog(log);
    return;
  }

  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Feedback API failed: ${res.status}`);
  }
}

export function getFeedbackLog(): FeedbackPayload[] {
  return readFeedbackLog();
}

export function getUserId(): string {
  const key = 'cardconcierge_user_id';
  let id = localStorage.getItem(key);
  if (!id) {
    id = `user_${crypto.randomUUID().slice(0, 8)}`;
    localStorage.setItem(key, id);
  }
  return id;
}
