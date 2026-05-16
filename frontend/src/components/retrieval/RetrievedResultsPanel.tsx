import type { RetrievedResult } from '../../types/retrieval.types';
import { CrisisCard } from './CrisisCard';

interface Props {
  results: RetrievedResult[];
  loading: boolean;
}

export function RetrievedResultsPanel({ results, loading }: Props) {
  return (
    <div className="middle-split-top">
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-title-icon">📊</span>
          Retrieved Crisis Data
          {results.length > 0 && (
            <span className="badge badge-blue" style={{ marginLeft: 6 }}>
              {results.length}
            </span>
          )}
        </div>
        {loading && <span className="spinner" />}
      </div>
      <div className="panel-body">
        {results.length === 0 && !loading ? (
          <div className="empty-state">
            <div className="empty-state-icon">🗄️</div>
            <p className="empty-state-text">
              Similar crisis records from the vector database will appear here after you send a message.
            </p>
          </div>
        ) : (
          results.map((r, i) => <CrisisCard key={r.id} result={r} index={i} />)
        )}
      </div>
    </div>
  );
}
