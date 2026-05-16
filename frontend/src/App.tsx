import './index.css';
import { useChat } from './hooks/useChat';
import { ChatPanel } from './components/chat/ChatPanel';
import { RetrievedResultsPanel } from './components/retrieval/RetrievedResultsPanel';
import { WebSearchPanel } from './components/search/WebSearchPanel';
import { DispatcherPanel } from './components/dispatch/DispatcherPanel';

export default function App() {
  const { messages, lastResponse, loading, error, send, clear } = useChat();

  return (
    <div className="app">
      {/* ── Header ───────────────────────────────────────── */}
      <header className="app-header">
        <div className="header-brand">
          <div className="header-icon">🚨</div>
          <div>
            <div className="header-title">
              Emergency <span>Response</span> System
            </div>
            <div className="header-subtitle">AI-Powered 911 Dispatcher · Gemini + ChromaDB</div>
          </div>
        </div>
        <div className="header-right">
          <div className="header-status">
            <span className="pulse-dot" />
            SYSTEM LIVE
          </div>
          <span className="badge badge-red" style={{ fontSize: 10 }}>
            ⚡ ACTIVE SESSION
          </span>
        </div>
      </header>

      {/* ── Main 3-column grid ────────────────────────────── */}
      <main className="app-grid">
        {/* Left: Chat */}
        <ChatPanel
          messages={messages}
          loading={loading}
          error={error}
          onSend={send}
          onClear={clear}
        />

        {/* Middle: Retrieval + Web Search stacked */}
        <div className="middle-split grid-col">
          <RetrievedResultsPanel
            results={lastResponse?.retrieved_results ?? []}
            loading={loading}
          />
          <WebSearchPanel
            search={lastResponse?.web_search ?? null}
            loading={loading}
          />
        </div>

        {/* Right: Dispatcher */}
        <DispatcherPanel
          state={lastResponse?.dispatcher_state ?? null}
          loading={loading}
        />
      </main>
    </div>
  );
}
