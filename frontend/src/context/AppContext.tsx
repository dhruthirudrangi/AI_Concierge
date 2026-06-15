import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { ChatMessage, RecommendedCard, UserPreferences } from '../types';
import { fetchRecommendations } from '../services/recommendApi';
import {
  generateGreeting,
  handleFollowUp,
  narrateRecommendations,
} from '../services/geminiService';

const PREFS_KEY = 'cardconcierge_preferences';

interface AppContextValue {
  preferences: UserPreferences | null;
  setPreferences: (prefs: UserPreferences) => void;
  messages: ChatMessage[];
  recommendations: RecommendedCard[];
  isLoading: boolean;
  error: string | null;
  initializeChat: () => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
  requestRecommendations: (query?: string) => Promise<void>;
  clearError: () => void;
}

const AppContext = createContext<AppContextValue | null>(null);

function loadPreferences(): UserPreferences | null {
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function savePreferences(prefs: UserPreferences): void {
  localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
}

function uid(): string {
  return crypto.randomUUID();
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferencesState] = useState<UserPreferences | null>(loadPreferences);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendedCard[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setPreferences = useCallback((prefs: UserPreferences) => {
    savePreferences(prefs);
    setPreferencesState(prefs);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  const initializeChat = useCallback(async () => {
    if (!preferences) return;
    setIsLoading(true);
    setError(null);

    const loadingMsg: ChatMessage = {
      id: uid(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      loading: true,
    };
    setMessages([loadingMsg]);

    try {
      const greeting = await generateGreeting(preferences);
      setMessages([
        {
          id: uid(),
          role: 'assistant',
          content: greeting,
          timestamp: new Date(),
        },
      ]);
      await fetchRecommendations({ preferences, topN: 10 }).then(async (res) => {
        setRecommendations(res.cards);
        const narration = await narrateRecommendations(preferences, res.cards);
        setMessages((prev) => [
          ...prev,
          {
            id: uid(),
            role: 'assistant',
            content: narration,
            timestamp: new Date(),
            cards: res.cards,
          },
        ]);
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to initialize chat');
      setMessages([
        {
          id: uid(),
          role: 'assistant',
          content: 'Sorry, something went wrong starting your session. Please try again.',
          timestamp: new Date(),
          error: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [preferences]);

  const requestRecommendations = useCallback(
    async (query?: string) => {
      if (!preferences) return;
      setIsLoading(true);
      setError(null);

      const loadingMsg: ChatMessage = {
        id: uid(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        loading: true,
      };
      setMessages((prev) => [...prev, loadingMsg]);

      try {
        const res = await fetchRecommendations({ preferences, query, topN: 10 });
        setRecommendations(res.cards);
        const narration = await narrateRecommendations(preferences, res.cards);
        setMessages((prev) => [
          ...prev.filter((m) => !m.loading),
          {
            id: uid(),
            role: 'assistant',
            content: narration,
            timestamp: new Date(),
            cards: res.cards,
          },
        ]);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to fetch recommendations');
        setMessages((prev) => [
          ...prev.filter((m) => !m.loading),
          {
            id: uid(),
            role: 'assistant',
            content: 'I could not fetch recommendations right now. Please try again.',
            timestamp: new Date(),
            error: true,
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [preferences],
  );

  const sendMessage = useCallback(
    async (text: string) => {
      if (!preferences || !text.trim()) return;

      const userMsg: ChatMessage = {
        id: uid(),
        role: 'user',
        content: text.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      setError(null);

      const loadingMsg: ChatMessage = {
        id: uid(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        loading: true,
      };
      setMessages((prev) => [...prev, loadingMsg]);

      const isRecommendQuery =
        /recommend|find|show|best|card|suggest|search/i.test(text) &&
        recommendations.length === 0;

      try {
        if (isRecommendQuery) {
          await requestRecommendations(text);
          return;
        }

        const reply = await handleFollowUp(
          text,
          [...messages, userMsg],
          preferences,
          recommendations,
        );

        setMessages((prev) => [
          ...prev.filter((m) => !m.loading),
          {
            id: uid(),
            role: 'assistant',
            content: reply,
            timestamp: new Date(),
            cards: recommendations.length ? recommendations : undefined,
          },
        ]);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to send message');
        setMessages((prev) => [
          ...prev.filter((m) => !m.loading),
          {
            id: uid(),
            role: 'assistant',
            content: 'Sorry, I had trouble responding. Please try again.',
            timestamp: new Date(),
            error: true,
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [preferences, messages, recommendations, requestRecommendations],
  );

  const value = useMemo(
    () => ({
      preferences,
      setPreferences,
      messages,
      recommendations,
      isLoading,
      error,
      initializeChat,
      sendMessage,
      requestRecommendations,
      clearError,
    }),
    [
      preferences,
      setPreferences,
      messages,
      recommendations,
      isLoading,
      error,
      initializeChat,
      sendMessage,
      requestRecommendations,
      clearError,
    ],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
