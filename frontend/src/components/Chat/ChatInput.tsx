import { useState } from 'react';
import { Send } from 'lucide-react';
import './ChatInput.css';

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const SUGGESTIONS = [
  'What card is best for travel?',
  'Compare my top 2 options',
  'Any cards with no annual fee?',
  'Refresh my recommendations',
];

export function ChatInput({ onSend, disabled, placeholder }: Props) {
  const [text, setText] = useState('');

  const submit = () => {
    if (!text.trim() || disabled) return;
    onSend(text);
    setText('');
  };

  return (
    <div className="chat-input-area">
      <div className="suggestions">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            className="suggestion-chip"
            disabled={disabled}
            onClick={() => onSend(s)}
          >
            {s}
          </button>
        ))}
      </div>
      <div className="chat-input-row">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          placeholder={placeholder ?? 'Ask about fees, benefits, or comparisons...'}
          disabled={disabled}
        />
        <button type="button" className="send-btn" onClick={submit} disabled={disabled || !text.trim()}>
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
