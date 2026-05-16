import type { DispatcherState } from '../../types/dispatch.types';
import { ResponderCard } from './ResponderCard';

interface Props {
  state: DispatcherState | null;
  loading: boolean;
}

const DISASTER_BADGE: Record<string, string> = {
  fire: 'badge-red',
  medical: 'badge-orange',
  police: 'badge-blue',
  earthquake: 'badge-yellow',
  flood: 'badge-blue',
  hurricane: 'badge-blue',
  rescue: 'badge-orange',
  tornado: 'badge-yellow',
  tsunami: 'badge-blue',
  explosion: 'badge-red',
  chemical: 'badge-yellow',
  emergency: 'badge-red',
};

export function DispatcherPanel({ state, loading }: Props) {
  return (
    <div className="grid-col">
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-title-icon">🤖</span>
          AI Dispatcher
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {loading && <span className="spinner" />}
          <span className="badge badge-green">
            <span className="pulse-dot" style={{ width: 6, height: 6 }} />
            ACTIVE
          </span>
        </div>
      </div>

      <div className="panel-body">
        {/* Status items */}
        <div className="dispatcher-status-row">
          <div className="ds-item">
            <div className="ds-label">📍 Identified Location</div>
            {state?.location ? (
              <div className="ds-value">{state.location}</div>
            ) : (
              <div className="ds-value none">Awaiting location…</div>
            )}
          </div>

          <div className="ds-item">
            <div className="ds-label">🔥 Emergency Type</div>
            {state?.disaster_type && state.disaster_type.length > 0 ? (
              <div className="ds-type-list">
                {state.disaster_type.map((t) => (
                  <span key={t} className={`badge ${DISASTER_BADGE[t] ?? 'badge-orange'}`}>
                    {t}
                  </span>
                ))}
              </div>
            ) : (
              <div className="ds-value none">Analyzing…</div>
            )}
          </div>
        </div>

        <div className="divider" />

        {/* AI Analysis */}
        <div>
          <div className="section-title">Dispatch Analysis</div>
          <div className="analysis-box">
            {state?.analysis || 'Analyzing conversation to determine dispatch requirements…'}
          </div>
        </div>

        <div className="divider" />

        {/* Responder units */}
        <div>
          <div className="section-title" style={{ marginBottom: 8 }}>
            Dispatched Units
            {state?.dispatched_units && state.dispatched_units.length > 0 && (
              <span className="badge badge-red" style={{ marginLeft: 8 }}>
                {state.dispatched_units.length}
              </span>
            )}
          </div>
          {state?.dispatched_units && state.dispatched_units.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {state.dispatched_units.map((r) => (
                <ResponderCard key={r.id} responder={r} />
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: '20px 0' }}>
              <div className="empty-state-icon" style={{ fontSize: 24 }}>📡</div>
              <p className="empty-state-text">Units will be dispatched once location and emergency type are confirmed.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
