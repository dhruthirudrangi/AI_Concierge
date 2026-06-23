import type { AnalyticsData } from '../types';

export const MOCK_ANALYTICS: AnalyticsData = {
  mrr: [
    { date: 'Week 1', tfidf: 0.42, bert: 0.58 },
    { date: 'Week 2', tfidf: 0.45, bert: 0.62 },
    { date: 'Week 3', tfidf: 0.48, bert: 0.67 },
    { date: 'Week 4', tfidf: 0.51, bert: 0.71 },
    { date: 'Week 5', tfidf: 0.53, bert: 0.74 },
    { date: 'Week 6', tfidf: 0.55, bert: 0.78 },
  ],
  ndcg: [
    { k: 1, tfidf: 0.72, bert: 0.85 },
    { k: 3, tfidf: 0.68, bert: 0.82 },
    { k: 5, tfidf: 0.65, bert: 0.79 },
    { k: 10, tfidf: 0.61, bert: 0.76 },
  ],
  ctr: [
    { date: 'Mon', impressions: 1200, clicks: 84, rate: 7.0 },
    { date: 'Tue', impressions: 1350, clicks: 108, rate: 8.0 },
    { date: 'Wed', impressions: 1100, clicks: 99, rate: 9.0 },
    { date: 'Thu', impressions: 1450, clicks: 130, rate: 9.0 },
    { date: 'Fri', impressions: 1600, clicks: 176, rate: 11.0 },
    { date: 'Sat', impressions: 980, clicks: 88, rate: 9.0 },
    { date: 'Sun', impressions: 870, clicks: 70, rate: 8.0 },
  ],
  embeddingHeatmap: {
    queryLabels: [
      'travel rewards',
      'cashback groceries',
      'business expenses',
      'dining delivery',
    ],
    cardLabels: [
      'AeroVoyage',
      'CashBack',
      'Gourmet',
      'FuelSaver',
      'ShopSmart',
      'BizPro',
    ],
    tfidf: [
      [0.82, 0.21, 0.35, 0.18, 0.24, 0.31],
      [0.19, 0.88, 0.42, 0.55, 0.38, 0.22],
      [0.28, 0.33, 0.45, 0.29, 0.51, 0.79],
      [0.31, 0.26, 0.91, 0.22, 0.34, 0.27],
    ],
    bert: [
      [0.94, 0.38, 0.52, 0.29, 0.41, 0.48],
      [0.35, 0.92, 0.58, 0.62, 0.55, 0.33],
      [0.42, 0.48, 0.61, 0.38, 0.67, 0.91],
      [0.45, 0.41, 0.96, 0.35, 0.49, 0.39],
    ],
  },
};
