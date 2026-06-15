import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { MOCK_ANALYTICS } from '../../mock/analytics';
import './MetricsCharts.css';

export function MetricsCharts() {
  const { mrr, ndcg, ctr } = MOCK_ANALYTICS;

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <h3>Mean Reciprocal Rank (MRR)</h3>
        <p className="metric-desc">TF-IDF vs BERT over evaluation weeks</p>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={mrr}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="tfidf" name="TF-IDF" stroke="#6366f1" strokeWidth={2} />
            <Line type="monotone" dataKey="bert" name="BERT" stroke="#10b981" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="metric-card">
        <h3>NDCG @ K</h3>
        <p className="metric-desc">Ranking quality at different cutoffs</p>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={ndcg}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="k" tickFormatter={(v) => `@${v}`} tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="tfidf" name="TF-IDF" fill="#6366f1" radius={[4, 4, 0, 0]} />
            <Bar dataKey="bert" name="BERT" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="metric-card full-width">
        <h3>Click-Through Rate</h3>
        <p className="metric-desc">Daily impressions vs clicks on Apply CTA</p>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={ctr}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
            <YAxis yAxisId="right" orientation="right" tickFormatter={(v) => `${v}%`} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value, name) => (name === 'rate' ? `${value}%` : value)} />
            <Legend />
            <Bar yAxisId="left" dataKey="impressions" name="Impressions" fill="#94a3b8" radius={[4, 4, 0, 0]} />
            <Bar yAxisId="left" dataKey="clicks" name="Clicks" fill="#6366f1" radius={[4, 4, 0, 0]} />
            <Line yAxisId="right" type="monotone" dataKey="rate" name="CTR %" stroke="#f59e0b" strokeWidth={2} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
