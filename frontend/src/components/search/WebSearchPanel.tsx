import type { WebSearchResult } from '../../types/search.types';

interface Props {
  search: WebSearchResult | null;
  loading: boolean;
}

export function WebSearchPanel({ search, loading }: Props) {
  const hasResults =
    search?.enabled &&
    (search.primary_results?.answer || (search.primary_results?.results?.length ?? 0) > 0);

  return (
    <div className="middle-split-bottom">
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-title-icon">🔍</span>
          Real-Time Intelligence
        </div>
        {loading && <span className="spinner" />}
      </div>

      <div className="panel-body" style={{ padding: '10px 14px', gap: 8 }}>
        {!search || !search.enabled ? (
          <div className="empty-state" style={{ padding: '16px 0' }}>
            <div className="empty-state-icon" style={{ fontSize: 22 }}>🌐</div>
            <p className="empty-state-text">Web search results will appear here.</p>
          </div>
        ) : search.error ? (
          <div className="search-answer" style={{ borderColor: 'rgba(255,45,70,0.25)', background: 'rgba(255,45,70,0.06)' }}>
            ⚠️ Search error: {search.error}
          </div>
        ) : hasResults ? (
          <>
            {search.primary_results?.answer && (
              <div className="search-answer">{search.primary_results.answer}</div>
            )}
            {search.primary_results?.results && search.primary_results.results.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {search.primary_results.results.slice(0, 3).map((src, i) => (
                  <a
                    key={i}
                    className="search-source"
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={src.title}
                  >
                    <span className="search-source-dot" />
                    {src.title}
                  </a>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="empty-state" style={{ padding: '16px 0' }}>
            <p className="empty-state-text">No relevant web results found.</p>
          </div>
        )}
      </div>
    </div>
  );
}
