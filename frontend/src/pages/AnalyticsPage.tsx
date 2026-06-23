import { MetricsCharts } from '../components/Analytics/MetricsCharts';
import { EmbeddingHeatmap } from '../components/Analytics/EmbeddingHeatmap';
import { getFeedbackLog } from '../services/feedbackApi';
import './AnalyticsPage.css';

export function AnalyticsPage() {
  const feedbackCount = getFeedbackLog().length;

  return (
    <div className="analytics-page">
      <header className="analytics-header">
        <h1>Analytics Dashboard</h1>
        <p>Recommendation quality metrics — TF-IDF vs BERT embedding comparison</p>
      </header>

      <div className="stat-cards">
        <div className="stat-card">
          <span className="stat-value">0.78</span>
          <span className="stat-label">Best MRR (BERT)</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">0.85</span>
          <span className="stat-label">NDCG@1 (BERT)</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">11%</span>
          <span className="stat-label">Peak CTR</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{feedbackCount}</span>
          <span className="stat-label">User Feedback Events</span>
        </div>
      </div>

      <MetricsCharts />
      <EmbeddingHeatmap />
    </div>
  );
}
