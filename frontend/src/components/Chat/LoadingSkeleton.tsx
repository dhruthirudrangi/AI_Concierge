import './LoadingSkeleton.css';

export function LoadingSkeleton() {
  return (
    <div className="skeleton-lines" aria-label="Loading response">
      <div className="skeleton-line wide" />
      <div className="skeleton-line medium" />
      <div className="skeleton-line narrow" />
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="card-skeleton" aria-label="Loading cards">
      <div className="skeleton-block header" />
      <div className="skeleton-line wide" />
      <div className="skeleton-line medium" />
      <div className="skeleton-line narrow" />
      <div className="skeleton-block btn" />
    </div>
  );
}
