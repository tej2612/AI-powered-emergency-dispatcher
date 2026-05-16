import { useState, useRef } from 'react';

interface Props {
  onSend: (message: string, enableWebSearch: boolean) => void;
  onClear: () => void;
  loading: boolean;
}

export function MessageInput({ onSend, onClear, loading }: Props) {
  const [value, setValue] = useState('');
  const [webSearch, setWebSearch] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (!value.trim() || loading) return;
    onSend(value.trim(), webSearch);
    setValue('');
    inputRef.current?.focus();
  };

  return (
    <div className="chat-input-area">
      <div className="chat-input-row">
        <input
          id="emergency-input"
          ref={inputRef}
          className="chat-input"
          type="text"
          placeholder="Describe the emergency situation..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          disabled={loading}
          autoFocus
        />
        <button
          id="send-btn"
          className="btn btn-primary"
          onClick={handleSend}
          disabled={loading || !value.trim()}
          style={{ minWidth: 100 }}
        >
          {loading ? (
            <><span className="spinner" style={{ width: 14, height: 14 }} /> Sending…</>
          ) : (
            '🚨 Send'
          )}
        </button>
      </div>
      <div className="chat-input-footer">
        <label className="toggle-row" htmlFor="web-search-toggle">
          <span className="toggle">
            <input
              id="web-search-toggle"
              type="checkbox"
              checked={webSearch}
              onChange={(e) => setWebSearch(e.target.checked)}
            />
            <span className="toggle-slider" />
          </span>
          🔍 Real-time web search
        </label>
        <button
          id="clear-btn"
          className="btn btn-ghost"
          onClick={onClear}
          style={{ padding: '6px 12px', fontSize: 11 }}
        >
          Clear
        </button>
      </div>
    </div>
  );
}
