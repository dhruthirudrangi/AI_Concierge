import { useState } from 'react';
import { MOCK_ANALYTICS } from '../../mock/analytics';
import './EmbeddingHeatmap.css';

type Model = 'tfidf' | 'bert';

function getColor(value: number): string {
  const hue = value * 120;
  return `hsl(${hue}, 70%, ${40 + value * 20}%)`;
}

export function EmbeddingHeatmap() {
  const [model, setModel] = useState<Model>('bert');
  const { queryLabels, cardLabels, tfidf, bert } = MOCK_ANALYTICS.embeddingHeatmap;
  const matrix = model === 'tfidf' ? tfidf : bert;

  return (
    <div className="heatmap-card">
      <div className="heatmap-header">
        <div>
          <h3>Embedding Similarity Heatmap</h3>
          <p className="metric-desc">Query–card cosine similarity: TF-IDF vs BERT</p>
        </div>
        <div className="model-toggle">
          <button
            type="button"
            className={model === 'tfidf' ? 'active' : ''}
            onClick={() => setModel('tfidf')}
          >
            TF-IDF
          </button>
          <button
            type="button"
            className={model === 'bert' ? 'active' : ''}
            onClick={() => setModel('bert')}
          >
            BERT
          </button>
        </div>
      </div>

      <div className="heatmap-wrapper">
        <table className="heatmap-table">
          <thead>
            <tr>
              <th className="corner" />
              {cardLabels.map((label) => (
                <th key={label}>{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, ri) => (
              <tr key={queryLabels[ri]}>
                <th className="row-label">{queryLabels[ri]}</th>
                {row.map((val, ci) => (
                  <td key={ci}>
                    <div
                      className="heat-cell"
                      style={{ background: getColor(val) }}
                      title={`${queryLabels[ri]} × ${cardLabels[ci]}: ${val.toFixed(2)}`}
                    >
                      {val.toFixed(2)}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="heatmap-legend">
        <span>Low (0.0)</span>
        <div className="legend-gradient" />
        <span>High (1.0)</span>
      </div>
    </div>
  );
}
