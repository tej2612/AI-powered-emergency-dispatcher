import { useRef, useEffect } from 'react';
import type { ConversationTurn } from '../../types/chat.types';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';

interface Props {
  messages: ConversationTurn[];
  loading: boolean;
  error: string | null;
  onSend: (message: string, enableWebSearch: boolean) => void;
  onClear: () => void;
}

export function ChatPanel({ messages, loading, error, onSend, onClear }: Props) {
  const threadRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight;
    }
  }, [messages, loading]);

  return (
    <div className="grid-col">
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-title-icon">🎙️</span>
          Emergency Call
        </div>
        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--text-muted)' }}>
            <span className="spinner" />
            Processing…
          </div>
        )}
      </div>

      <div className="chat-thread" ref={threadRef}>
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">🚨</div>
            <p style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Emergency Response AI</p>
            <p style={{ fontSize: 12 }}>
              Describe the emergency situation below. The AI dispatcher will guide you and coordinate resources.
            </p>
          </div>
        ) : (
          messages.map((m, i) => <MessageBubble key={i} turn={m} />)
        )}

        {loading && (
          <div className="message message-assistant">
            <span className="message-role">🚨 Dispatcher</span>
            <div className="message-thinking">
              <span>Analyzing…</span>
              <span className="thinking-dots">
                <span /><span /><span />
              </span>
            </div>
          </div>
        )}

        {error && (
          <div style={{
            padding: '10px 14px', borderRadius: 'var(--radius-md)',
            background: 'rgba(255,45,70,0.08)', border: '1px solid rgba(255,45,70,0.25)',
            fontSize: 12.5, color: 'var(--red)',
          }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      <MessageInput onSend={onSend} onClear={onClear} loading={loading} />
    </div>
  );
}
