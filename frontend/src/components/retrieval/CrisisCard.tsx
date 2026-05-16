import type { RetrievedResult } from '../../types/retrieval.types';

interface Props {
  result: RetrievedResult;
  index: number;
}

const DAMAGE_CLASS: Record<string, string> = {
  HIGH: 'badge-red',
  MEDIUM: 'badge-orange',
  LOW: 'badge-green',
};

const DISASTER_EMOJI: Record<string, string> = {
  Wildfire: '🔥',
  Earthquake: '🌋',
  Flood: '🌊',
  Hurricane: '🌀',
  Other: '⚠️',
};

export function CrisisCard({ result, index }: Props) {
  const emoji = DISASTER_EMOJI[result.disaster_type] ?? '⚠️';
  const damageClass = DAMAGE_CLASS[result.image_damage ?? ''] ?? 'badge-blue';
  const scorePercent = Math.round(result.score * 100);

  return (
    <div className="crisis-card" id={`crisis-card-${index}`}>
      {result.image_base64 ? (
        <img
          className="crisis-card-img"
          src={result.image_base64}
          alt={result.image_caption || 'Crisis image'}
          loading="lazy"
        />
      ) : (
        <div className="crisis-card-img-placeholder">{emoji}</div>
      )}
      <div className="crisis-card-body">
        <div className="crisis-card-meta">
          <span className={`badge ${damageClass}`}>
            {result.image_damage || 'N/A'}
          </span>
          <span className="badge badge-blue">{emoji} {result.disaster_type}</span>
          {result.extracted_location && (
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              📍 {result.extracted_location}
            </span>
          )}
        </div>
        <p className="crisis-card-text">
          {result.tweet_text.length > 160
            ? result.tweet_text.slice(0, 157) + '…'
            : result.tweet_text}
        </p>
        <div className="crisis-card-footer">
          <div className="score-bar-wrap">
            <div className="score-bar" style={{ width: `${scorePercent}%` }} />
          </div>
          <span className="score-val mono">{result.score.toFixed(3)}</span>
        </div>
      </div>
    </div>
  );
}
