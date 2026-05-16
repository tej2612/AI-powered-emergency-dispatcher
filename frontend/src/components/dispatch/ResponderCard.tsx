import type { Responder } from '../../types/dispatch.types';

interface Props {
  responder: Responder;
}

const UNIT_ICON: Record<string, string> = {
  FR: '🚒',
  MD: '🚑',
  PD: '🚔',
  RS: '🛟',
  FD: '🌊',
  EQ: '⛑️',
};

export function ResponderCard({ responder }: Props) {
  const prefix = responder.id.split('-')[0];
  const icon = UNIT_ICON[prefix] ?? '🆘';

  return (
    <div className="responder-card">
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 18 }}>{icon}</span>
        <div>
          <div className="responder-name">{responder.name}</div>
          <div className="responder-units">{responder.units} unit{responder.units !== 1 ? 's' : ''} · {responder.id}</div>
        </div>
      </div>
      <div className="responder-eta">ETA {responder.eta}</div>
    </div>
  );
}
