import { useState } from 'react';

const SESSION_KEY = 'er_session_id';

export function useSession(): string {
  const [sessionId] = useState<string>(() => {
    const stored = sessionStorage.getItem(SESSION_KEY);
    if (stored) return stored;
    const fresh = crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY, fresh);
    return fresh;
  });
  return sessionId;
}
