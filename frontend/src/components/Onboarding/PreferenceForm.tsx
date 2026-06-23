import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, DollarSign, Globe, Tag } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { REGIONS, SPENDING_CATEGORIES, type UserPreferences } from '../../types';
import './PreferenceForm.css';

const DEFAULT_PREFS: UserPreferences = {
  categories: ['Travel', 'Dining'],
  monthlySpend: 3000,
  region: 'North America',
  balance: 5000,
};

export function PreferenceForm() {
  const { preferences, setPreferences } = useApp();
  const navigate = useNavigate();
  const [form, setForm] = useState<UserPreferences>(preferences ?? DEFAULT_PREFS);
  const [errors, setErrors] = useState<string[]>([]);

  const toggleCategory = (cat: string) => {
    setForm((prev) => ({
      ...prev,
      categories: prev.categories.includes(cat)
        ? prev.categories.filter((c) => c !== cat)
        : [...prev.categories, cat],
    }));
  };

  const validate = (): boolean => {
    const errs: string[] = [];
    if (form.categories.length === 0) errs.push('Select at least one spending category.');
    if (form.monthlySpend <= 0) errs.push('Monthly spend must be greater than 0.');
    if (form.balance < 0) errs.push('Balance cannot be negative.');
    setErrors(errs);
    return errs.length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setPreferences(form);
    navigate('/concierge');
  };

  return (
    <div className="onboarding-page">
      <div className="onboarding-header">
        <h1>Tell us about your spending</h1>
        <p>We'll personalize card recommendations to your categories, budget, and region.</p>
      </div>

      <form className="preference-form" onSubmit={handleSubmit}>
        <section className="form-section">
          <div className="section-label">
            <Tag size={18} />
            <h2>Spending categories</h2>
          </div>
          <div className="category-grid">
            {SPENDING_CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                className={`category-chip ${form.categories.includes(cat) ? 'selected' : ''}`}
                onClick={() => toggleCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        </section>

        <section className="form-section">
          <div className="section-label">
            <DollarSign size={18} />
            <h2>Monthly spend & balance</h2>
          </div>
          <div className="input-row">
            <label>
              Monthly spend ($)
              <input
                type="number"
                min={0}
                value={form.monthlySpend}
                onChange={(e) =>
                  setForm((p) => ({ ...p, monthlySpend: Number(e.target.value) }))
                }
              />
            </label>
            <label>
              Account balance ($)
              <input
                type="number"
                min={0}
                value={form.balance}
                onChange={(e) =>
                  setForm((p) => ({ ...p, balance: Number(e.target.value) }))
                }
              />
            </label>
          </div>
        </section>

        <section className="form-section">
          <div className="section-label">
            <Globe size={18} />
            <h2>Region</h2>
          </div>
          <div className="region-grid">
            {REGIONS.map((region) => (
              <label key={region} className={`region-option ${form.region === region ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="region"
                  value={region}
                  checked={form.region === region}
                  onChange={() => setForm((p) => ({ ...p, region }))}
                />
                {region}
              </label>
            ))}
          </div>
        </section>

        {errors.length > 0 && (
          <ul className="form-errors">
            {errors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        )}

        <button type="submit" className="btn-primary">
          Continue to Concierge
          <ArrowRight size={18} />
        </button>
      </form>
    </div>
  );
}
