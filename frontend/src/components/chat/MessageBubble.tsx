import type { ConversationTurn } from '../../types/chat.types';

interface Props {
  turn: ConversationTurn;
}

export function MessageBubble({ turn }: Props) {
  const isUser = turn.role === 'user';
  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'}`}>
      <span className="message-role">{isUser ? '🎙️ Caller' : '🚨 Dispatcher'}</span>
      <div className="message-bubble">{turn.content}</div>
    </div>
  );
}
