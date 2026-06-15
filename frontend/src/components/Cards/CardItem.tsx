import { useState } from 'react';
import { ExternalLink, ThumbsDown, ThumbsUp } from 'lucide-react';
import type { RecommendedCard } from '../../types';
import { getUserId, submitFeedback } from '../../services/feedbackApi';
import './CardItem.css';

interface Props {
  card: RecommendedCard;
}

export function CardItem({ card }: Props) {
  const [feedback, setFeedback] = useState<'like' | 'dislike' | null>(null);
  const [feedbackError, setFeedbackError] = useState(false);

  const handleFeedback = async (type: 'like' | 'dislike') => {
    setFeedback(type);
    setFeedbackError(false);
    try {
      await submitFeedback({
        cardId: card.id,
        cardName: card.name,
        userId: getUserId(),
        feedback: type,
        timestamp: new Date().toISOString(),
      });
    } catch {
      setFeedbackError(true);
      setFeedback(null);
    }
  };

  const scorePercent = Math.round(card.score * 100);

  return (
    <article className="card-item">
      <div className="card-header">
        <div>
          <span className="card-rank">#{card.rank}</span>
          <h3>{card.name}</h3>
          <p className="card-issuer">{card.issuer}</p>
        </div>
        <div className={`score-badge ${scorePercent >= 80 ? 'high' : scorePercent >= 60 ? 'mid' : 'low'}`}>
          {scorePercent}%
          <span>match</span>
        </div>
      </div>

      <p className="card-description">{card.description}</p>

      <ul className="card-benefits">
        {card.benefits.slice(0, 3).map((b) => (
          <li key={b}>{b}</li>
        ))}
      </ul>

      <div className="card-meta">
        <span>${card.annualFee}/yr fee</span>
        <span>Sim: {(card.similarityScore * 100).toFixed(0)}%</span>
      </div>

      <div className="card-actions">
        <a
          href={card.applyUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="apply-btn"
          onClick={() => {
            submitFeedback({
              cardId: card.id,
              cardName: card.name,
              userId: getUserId(),
              feedback: 'like',
              timestamp: new Date().toISOString(),
            }).catch(() => {});
          }}
        >
          Apply Now
          <ExternalLink size={14} />
        </a>
        <div className="feedback-btns">
          <button
            type="button"
            className={feedback === 'like' ? 'active like' : ''}
            onClick={() => handleFeedback('like')}
            aria-label="Like"
          >
            <ThumbsUp size={16} />
          </button>
          <button
            type="button"
            className={feedback === 'dislike' ? 'active dislike' : ''}
            onClick={() => handleFeedback('dislike')}
            aria-label="Dislike"
          >
            <ThumbsDown size={16} />
          </button>
        </div>
      </div>
      {feedbackError && <p className="feedback-error">Could not save feedback</p>}
    </article>
  );
}
