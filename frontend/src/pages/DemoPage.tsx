import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  CreditCard,
  MessageCircle,
  Play,
  UserCircle,
} from 'lucide-react';
import './DemoPage.css';

const STEPS = [
  {
    id: 1,
    title: 'Problem',
    icon: CreditCard,
    content:
      'Users face 100+ credit cards with overlapping benefits. Traditional filters miss semantic intent — ' +
      'someone searching "frequent flyer perks" may miss cards labeled "airline miles."',
    route: null,
  },
  {
    id: 2,
    title: 'User Onboarding',
    icon: UserCircle,
    content:
      'Collect spending categories, monthly budget, account balance, and region to personalize eligibility and scoring.',
    route: '/onboarding',
  },
  {
    id: 3,
    title: 'AI Concierge Chat',
    icon: MessageCircle,
    content:
      'Gemini-powered concierge greets users, narrates top-N recommendations with reasoning, and handles multi-turn follow-ups.',
    route: '/concierge',
  },
  {
    id: 4,
    title: 'Card Carousel + Feedback',
    icon: CreditCard,
    content:
      'Top recommendations displayed with match scores, Apply CTA, and like/dislike feedback logged for re-ranking.',
    route: '/concierge',
  },
  {
    id: 5,
    title: 'Analytics & Results',
    icon: BarChart3,
    content:
      'MRR, NDCG, and CTR charts plus TF-IDF vs BERT embedding heatmap demonstrate measurable ranking improvements.',
    route: '/analytics',
  },
  {
    id: 6,
    title: 'Architecture',
    icon: CheckCircle2,
    content:
      'React frontend → FastAPI /recommend → TF-IDF/BERT embeddings → FAISS index → Gemini LLM narration. ' +
      'MongoDB stores cards, embeddings, and feedback.',
    route: null,
  },
];

export function DemoPage() {
  const [activeStep, setActiveStep] = useState(0);
  const navigate = useNavigate();
  const step = STEPS[activeStep];

  return (
    <div className="demo-page">
      <header className="demo-header">
        <h1>Live Demo Walkthrough</h1>
        <p>End-to-end presentation flow: problem → solution → architecture → results</p>
      </header>

      <div className="demo-layout">
        <nav className="demo-steps">
          {STEPS.map((s, i) => (
            <button
              key={s.id}
              type="button"
              className={`demo-step-btn ${i === activeStep ? 'active' : ''} ${i < activeStep ? 'done' : ''}`}
              onClick={() => setActiveStep(i)}
            >
              <span className="step-num">{s.id}</span>
              {s.title}
            </button>
          ))}
        </nav>

        <div className="demo-content">
          <div className="demo-slide">
            <step.icon size={32} className="slide-icon" />
            <h2>{step.title}</h2>
            <p>{step.content}</p>

            {step.route && (
              <button type="button" className="demo-action" onClick={() => navigate(step.route!)}>
                Open {step.title}
                <ArrowRight size={16} />
              </button>
            )}
          </div>

          <div className="demo-controls">
            <button
              type="button"
              disabled={activeStep === 0}
              onClick={() => setActiveStep((s) => s - 1)}
            >
              Previous
            </button>
            {activeStep < STEPS.length - 1 ? (
              <button type="button" className="primary" onClick={() => setActiveStep((s) => s + 1)}>
                Next
                <ArrowRight size={16} />
              </button>
            ) : (
              <button type="button" className="primary" onClick={() => navigate('/concierge')}>
                <Play size={16} />
                Start Live Demo
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
