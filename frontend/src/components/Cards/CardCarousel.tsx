import { useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import type { RecommendedCard } from '../../types';
import { CardItem } from './CardItem';
import './CardCarousel.css';

interface Props {
  cards: RecommendedCard[];
}

export function CardCarousel({ cards }: Props) {
  const trackRef = useRef<HTMLDivElement>(null);

  const scroll = (dir: 'left' | 'right') => {
    const el = trackRef.current;
    if (!el) return;
    el.scrollBy({ left: dir === 'left' ? -340 : 340, behavior: 'smooth' });
  };

  if (cards.length === 0) return null;

  return (
    <div className="card-carousel">
      <div className="carousel-header">
        <h4>Top {cards.length} Recommendations</h4>
        <div className="carousel-nav">
          <button type="button" onClick={() => scroll('left')} aria-label="Previous cards">
            <ChevronLeft size={20} />
          </button>
          <button type="button" onClick={() => scroll('right')} aria-label="Next cards">
            <ChevronRight size={20} />
          </button>
        </div>
      </div>
      <div className="carousel-track" ref={trackRef}>
        {cards.map((card) => (
          <CardItem key={card.id} card={card} />
        ))}
      </div>
    </div>
  );
}
