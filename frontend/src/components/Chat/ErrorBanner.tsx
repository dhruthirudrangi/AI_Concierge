import { AlertCircle, X } from 'lucide-react';
import './ErrorBanner.css';

interface Props {
  message: string;
  onDismiss?: () => void;
}

export function ErrorBanner({ message, onDismiss }: Props) {
  return (
    <div className="error-banner" role="alert">
      <AlertCircle size={18} />
      <span>{message}</span>
      {onDismiss && (
        <button type="button" className="error-dismiss" onClick={onDismiss} aria-label="Dismiss">
          <X size={16} />
        </button>
      )}
    </div>
  );
}
