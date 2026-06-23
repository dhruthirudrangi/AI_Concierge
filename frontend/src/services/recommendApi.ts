import { MOCK_CARDS } from '../mock/cards';
import type {
  RecommendRequest,
  RecommendResponse,
  RecommendedCard,
  UserPreferences,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

function categoryOverlap(cardCategories: string[], userCategories: string[]): number {
  if (userCategories.length === 0) return 0;
  const matches = userCategories.filter((c) => cardCategories.includes(c)).length;
  return matches / userCategories.length;
}

function textSimilarity(query: string, description: string, benefits: string[]): number {
  const text = `${description} ${benefits.join(' ')}`.toLowerCase();
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (terms.length === 0) return 0.5;
  const hits = terms.filter((t) => text.includes(t)).length;
  return hits / terms.length;
}

function computeBusinessWeight(
  card: (typeof MOCK_CARDS)[0],
  prefs: UserPreferences,
): number {
  let weight = 1.0;

  if (card.regions.includes(prefs.region) || card.regions.includes('Global')) {
    weight *= 1.2;
  } else {
    weight *= 0.3;
  }

  if (prefs.balance >= card.minBalance) {
    weight *= 1.15;
  } else {
    weight *= 0.5;
  }

  if (card.annualFee === 0 && prefs.monthlySpend < 2000) {
    weight *= 1.1;
  }

  if (prefs.monthlySpend > 5000 && card.annualFee > 400) {
    weight *= 1.25;
  }

  return Math.min(weight, 1.5);
}

function mockRecommend(request: RecommendRequest): RecommendResponse {
  const { preferences, query = '', topN = 10 } = request;

  const eligible = MOCK_CARDS.filter(
    (card) =>
      (card.regions.includes(preferences.region) || card.regions.includes('Global')) &&
      preferences.balance >= card.minBalance * 0.5,
  );

  const scored: RecommendedCard[] = eligible
    .map((card) => {
      const catScore = categoryOverlap(card.categories, preferences.categories);
      const simScore = query
        ? textSimilarity(query, card.description, card.benefits)
        : catScore * 0.7 + 0.3;
      const businessWeight = computeBusinessWeight(card, preferences);
      const score = simScore * businessWeight;

      return {
        ...card,
        similarityScore: Math.round(simScore * 100) / 100,
        businessRuleWeight: Math.round(businessWeight * 100) / 100,
        score: Math.round(score * 100) / 100,
        rank: 0,
      };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, topN)
    .map((card, i) => ({ ...card, rank: i + 1 }));

  return {
    cards: scored,
    model: query.length > 20 ? 'bert' : 'tfidf',
    timestamp: new Date().toISOString(),
  };
}

export async function fetchRecommendations(
  request: RecommendRequest,
): Promise<RecommendResponse> {
  if (USE_MOCK || !API_BASE) {
    await new Promise((r) => setTimeout(r, 600 + Math.random() * 400));
    return mockRecommend(request);
  }

  const res = await fetch(`${API_BASE}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    throw new Error(`Recommend API failed: ${res.status}`);
  }

  return res.json();
}
