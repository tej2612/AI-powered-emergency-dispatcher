import { useState, useCallback, useRef, useEffect } from 'react';
import { sendMessage, clearSession } from '../api/chat.api';
import type { ConversationTurn, ChatResponse } from '../types/chat.types';
import { useSession } from './useSession';

export function useChat() {
  const sessionId = useSession();
  const [messages, setMessages] = useState<ConversationTurn[]>([]);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const threadRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const send = useCallback(
    async (message: string, enableWebSearch = true) => {
      if (!message.trim() || loading) return;
      setError(null);
      setLoading(true);
      setMessages((prev) => [...prev, { role: 'user', content: message }]);

      try {
        const res = await sendMessage({
          session_id: sessionId,
          message,
          enable_web_search: enableWebSearch,
        });
        setMessages((prev) => [...prev, { role: 'assistant', content: res.response }]);
        setLastResponse(res);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Request failed';
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [sessionId, loading]
  );

  const clear = useCallback(async () => {
    await clearSession(sessionId).catch(() => {});
    setMessages([]);
    setLastResponse(null);
    setError(null);
  }, [sessionId]);

  return { sessionId, messages, lastResponse, loading, error, send, clear, threadRef };
}
