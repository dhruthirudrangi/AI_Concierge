# CardConcierge — Member 3 (Frontend + LLM Concierge)

AI-powered credit card recommendation frontend with Gemini LLM integration.

## Features

- **Onboarding** — preference form (categories, spend, balance, region)
- **Chat UI** — conversation thread, message bubbles, loading skeletons, error states
- **Card carousel** — top-N cards with score badges, Apply CTA, like/dislike feedback
- **LLM concierge** — Gemini-powered greeting, narration, multi-turn follow-ups
- **Analytics dashboard** — MRR, NDCG, CTR charts + TF-IDF vs BERT heatmap
- **Demo walkthrough** — presentation slides for live demo

## Setup

```bash
cd frontend
npm install
cp .env.example .env
# Add your Gemini API key to .env
npm run dev
```

Open http://localhost:5173

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_GEMINI_API_KEY` | Google Gemini API key (required for live LLM) |
| `VITE_USE_MOCK` | Set to `false` when Member 1/2 backend is ready |
| `VITE_API_BASE_URL` | FastAPI backend URL (e.g. `http://localhost:8000`) |

Without `VITE_GEMINI_API_KEY`, the app uses intelligent mock LLM responses.

## Mock Mode

By default, `/recommend` and `/feedback` are mocked locally:
- 12 sample credit cards with scoring logic
- Feedback stored in `localStorage`
- Analytics uses pre-built evaluation data

When your teammates finish the backend, set:

```
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://localhost:8000
```

## Routes

| Path | Page |
|------|------|
| `/onboarding` | User preference form |
| `/concierge` | Chat + card recommendations |
| `/analytics` | MRR, NDCG, CTR, heatmap |
| `/demo` | Live demo presentation flow |

## Project Structure

```
src/
  components/   # UI components (Chat, Cards, Analytics, Onboarding)
  context/      # App state (preferences, messages, recommendations)
  mock/         # Mock cards + analytics data
  pages/        # Route pages
  services/     # recommendApi, feedbackApi, geminiService
  types/        # TypeScript interfaces
```
