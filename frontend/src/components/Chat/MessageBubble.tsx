import type { ChatMessage as ChatMessageType } from '../../types';
import { CardCarousel } from '../Cards/CardCarousel';
import { LoadingSkeleton } from './LoadingSkeleton';
import './MessageBubble.css';

interface Props {
  message: ChatMessageType;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user';

  if (message.loading) {
    return (
      <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
        <div className="bubble assistant-bubble">
          <LoadingSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`bubble ${isUser ? 'user-bubble' : 'assistant-bubble'} ${message.error ? 'error' : ''}`}>
        <div className="bubble-content">
          {message.content.split('\n').map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
        <span className="bubble-time">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
      {message.cards && message.cards.length > 0 && (
        <div className="message-carousel">
          <CardCarousel cards={message.cards} />
        </div>
      )}
    </div>
  );
}
