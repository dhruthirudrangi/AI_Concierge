export interface UserPreferences {
  categories: string[];
  monthlySpend: number;
  region: string;
  balance: number;
}

export interface CreditCard {
  id: string;
  name: string;
  issuer: string;
  benefits: string[];
  description: string;
  annualFee: number;
  minBalance: number;
  regions: string[];
  categories: string[];
  applyUrl: string;
}

export interface RecommendedCard extends CreditCard {
  score: number;
  similarityScore: number;
  businessRuleWeight: number;
  rank: number;
}

export interface RecommendRequest {
  preferences: UserPreferences;
  query?: string;
  topN?: number;
}

export interface RecommendResponse {
  cards: RecommendedCard[];
  model: 'tfidf' | 'bert';
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  cards?: RecommendedCard[];
  error?: boolean;
  loading?: boolean;
}

export interface FeedbackPayload {
  cardId: string;
  cardName: string;
  userId: string;
  feedback: 'like' | 'dislike';
  timestamp: string;
}

export interface AnalyticsData {
  mrr: { date: string; tfidf: number; bert: number }[];
  ndcg: { k: number; tfidf: number; bert: number }[];
  ctr: { date: string; impressions: number; clicks: number; rate: number }[];
  embeddingHeatmap: {
    queryLabels: string[];
    cardLabels: string[];
    tfidf: number[][];
    bert: number[][];
  };
}

export const SPENDING_CATEGORIES = [
  'Travel',
  'Dining',
  'Groceries',
  'Gas',
  'Shopping',
  'Entertainment',
  'Cashback',
  'Business',
] as const;

export const REGIONS = [
  'North America',
  'Europe',
  'Asia Pacific',
  'Global',
] as const;
