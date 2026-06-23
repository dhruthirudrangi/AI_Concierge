import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { RefreshCw } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { ChatThread } from '../components/Chat/ChatThread';
import { ChatInput } from '../components/Chat/ChatInput';
import { ErrorBanner } from '../components/Chat/ErrorBanner';
import { CardCarousel } from '../components/Cards/CardCarousel';
import { CardSkeleton } from '../components/Chat/LoadingSkeleton';
import './ConciergePage.css';

export function ConciergePage() {
  const {
    preferences,
    messages,
    recommendations,
    isLoading,
    error,
    initializeChat,
    sendMessage,
    requestRecommendations,
    clearError,
  } = useApp();
  const initialized = useRef(false);

  useEffect(() => {
    if (preferences && !initialized.current && messages.length === 0) {
      initialized.current = true;
      initializeChat();
    }
  }, [preferences, messages.length, initializeChat]);

  if (!preferences) {
    return (
      <div className="concierge-empty">
        <h2>Set your preferences first</h2>
        <p>Complete onboarding so we can personalize your recommendations.</p>
        <Link to="/onboarding" className="btn-primary-link">
          Go to Preferences
        </Link>
      </div>
    );
  }

  const handleSend = (text: string) => {
    if (/refresh|update recommendations/i.test(text)) {
      requestRecommendations();
    } else {
      sendMessage(text);
    }
  };

  return (
    <div className="concierge-page">
      <aside className="concierge-sidebar">
        <div className="profile-summary">
          <h3>Your Profile</h3>
          <dl>
            <dt>Categories</dt>
            <dd>{preferences.categories.join(', ')}</dd>
            <dt>Monthly spend</dt>
            <dd>${preferences.monthlySpend.toLocaleString()}</dd>
            <dt>Balance</dt>
            <dd>${preferences.balance.toLocaleString()}</dd>
            <dt>Region</dt>
            <dd>{preferences.region}</dd>
          </dl>
          <Link to="/onboarding" className="edit-link">
            Edit preferences
          </Link>
        </div>

        {isLoading && recommendations.length === 0 ? (
          <div className="sidebar-cards">
            <CardSkeleton />
          </div>
        ) : recommendations.length > 0 ? (
          <div className="sidebar-cards desktop-only">
            <CardCarousel cards={recommendations.slice(0, 5)} />
          </div>
        ) : null}
      </aside>

      <main className="concierge-main">
        <header className="concierge-header">
          <div>
            <h1>Card Concierge</h1>
            <p>Ask questions, compare cards, and explore personalized matches.</p>
          </div>
          <button
            type="button"
            className="refresh-btn"
            onClick={() => requestRecommendations()}
            disabled={isLoading}
          >
            <RefreshCw size={16} className={isLoading ? 'spin' : ''} />
            Refresh
          </button>
        </header>

        {error && <ErrorBanner message={error} onDismiss={clearError} />}

        <ChatThread messages={messages} />
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </main>
    </div>
  );
}
