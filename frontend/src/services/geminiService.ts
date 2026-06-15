import { GoogleGenerativeAI } from '@google/generative-ai';
import type { ChatMessage, RecommendedCard, UserPreferences } from '../types';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY ?? '';

const SYSTEM_PROMPT = `You are CardConcierge, a friendly and knowledgeable AI credit card advisor.

Your role:
- Greet users warmly and proactively suggest how you can help based on their preferences
- Explain credit card recommendations in clear, natural language (not bullet dumps unless asked)
- Provide reasoning: why each card fits their spending categories, region, and balance
- Answer follow-up questions about fees, benefits, comparisons, and trade-offs
- Be concise (2-4 short paragraphs max unless user asks for detail)
- Never invent cards not in the provided list
- If asked about cards not recommended, explain why alternatives may be better

Tone: professional, helpful, conversational — like a trusted financial advisor.`;

function buildCardContext(cards: RecommendedCard[]): string {
  if (cards.length === 0) return 'No cards recommended yet.';
  return cards
    .map(
      (c, i) =>
        `${i + 1}. ${c.name} (${c.issuer}) — Score: ${(c.score * 100).toFixed(0)}% | ` +
        `Fee: $${c.annualFee}/yr | Benefits: ${c.benefits.join('; ')} | ` +
        `Categories: ${c.categories.join(', ')}`,
    )
    .join('\n');
}

function buildPreferencesContext(prefs: UserPreferences): string {
  return (
    `User preferences:\n` +
    `- Spending categories: ${prefs.categories.join(', ')}\n` +
    `- Monthly spend: $${prefs.monthlySpend}\n` +
    `- Account balance: $${prefs.balance}\n` +
    `- Region: ${prefs.region}`
  );
}

function formatHistory(messages: ChatMessage[]): string {
  return messages
    .filter((m) => !m.loading && !m.error)
    .slice(-8)
    .map((m) => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`)
    .join('\n\n');
}

function mockResponse(
  type: 'greeting' | 'narration' | 'followup',
  prefs: UserPreferences,
  cards: RecommendedCard[],
  userMessage?: string,
): string {
  const top = cards[0];
  const categories = prefs.categories.join(', ');

  if (type === 'greeting') {
    return (
      `Welcome! I'm your CardConcierge assistant. Based on your profile — ` +
      `${categories} spending around $${prefs.monthlySpend}/month in ${prefs.region} — ` +
      `I can find cards that maximize your rewards.\n\n` +
      `Try asking: "What card is best for travel?" or "Compare my top 2 options." ` +
      `I'll walk you through each recommendation with clear reasoning.`
    );
  }

  if (type === 'narration' && top) {
    return (
      `Great news — I found ${cards.length} cards tailored to your profile!\n\n` +
      `My top pick is **${top.name}** from ${top.issuer} with a match score of ${(top.score * 100).toFixed(0)}%. ` +
      `It aligns strongly with your ${categories} spending` +
      (top.annualFee === 0 ? ' and has no annual fee.' : ` (annual fee: $${top.annualFee}).`) +
      ` Key perks include ${top.benefits.slice(0, 2).join(' and ')}.\n\n` +
      `Swipe through the carousel to see all matches. Tap Apply on any card you're interested in, ` +
      `or ask me to compare specific options!`
    );
  }

  if (type === 'followup' && userMessage) {
    const lower = userMessage.toLowerCase();
    if (lower.includes('fee') || lower.includes('annual')) {
      const noFee = cards.filter((c) => c.annualFee === 0);
      return noFee.length
        ? `Looking at annual fees: ${noFee.map((c) => `${c.name} ($0)`).join(', ')} have no annual fee. ` +
          `Given your $${prefs.monthlySpend}/mo spend, ${noFee[0]?.name ?? 'a no-fee card'} offers solid value without upfront cost.`
        : `All recommended cards have annual fees, but the rewards often offset them at your spend level. ` +
          `${top?.name ?? 'The top card'} at $${top?.annualFee ?? 0}/yr may still net positive if you use its bonus categories.`;
    }
    if (lower.includes('compare') || lower.includes('vs') || lower.includes('difference')) {
      const a = cards[0];
      const b = cards[1];
      if (a && b) {
        return (
          `Comparing **${a.name}** vs **${b.name}**:\n\n` +
          `${a.name} scores ${(a.score * 100).toFixed(0)}% with ${a.benefits[0]}. ` +
          `Annual fee: $${a.annualFee}.\n\n` +
          `${b.name} scores ${(b.score * 100).toFixed(0)}% with ${b.benefits[0]}. ` +
          `Annual fee: $${b.annualFee}.\n\n` +
          `For ${categories}, ${a.score >= b.score ? a.name : b.name} is the stronger fit.`
        );
      }
    }
    return (
      `Based on your ${categories} profile in ${prefs.region}, I'd highlight ${top?.name ?? 'your top match'}. ` +
      `Feel free to ask about fees, benefits, or how two cards compare!`
    );
  }

  return 'How can I help you find the right credit card today?';
}

async function callGemini(prompt: string): Promise<string> {
  if (!API_KEY) {
    throw new Error('NO_API_KEY');
  }

  const genAI = new GoogleGenerativeAI(API_KEY);
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.0-flash',
    systemInstruction: SYSTEM_PROMPT,
  });

  const result = await model.generateContent(prompt);
  return result.response.text();
}

export async function generateGreeting(
  prefs: UserPreferences,
): Promise<string> {
  const prompt =
    `${buildPreferencesContext(prefs)}\n\n` +
    `Generate a warm greeting (2-3 sentences) and one proactive suggestion for what the user could ask.`;

  try {
    return await callGemini(prompt);
  } catch {
    return mockResponse('greeting', prefs, []);
  }
}

export async function narrateRecommendations(
  prefs: UserPreferences,
  cards: RecommendedCard[],
): Promise<string> {
  const prompt =
    `${buildPreferencesContext(prefs)}\n\n` +
    `Recommended cards:\n${buildCardContext(cards)}\n\n` +
    `Narrate these recommendations naturally. Include greeting context, reasoning for the top pick, ` +
    `and invite the user to explore the carousel or ask follow-up questions.`;

  try {
    return await callGemini(prompt);
  } catch {
    return mockResponse('narration', prefs, cards);
  }
}

export async function handleFollowUp(
  userMessage: string,
  history: ChatMessage[],
  prefs: UserPreferences,
  cards: RecommendedCard[],
): Promise<string> {
  const prompt =
    `${buildPreferencesContext(prefs)}\n\n` +
    `Current recommendations:\n${buildCardContext(cards)}\n\n` +
    `Conversation so far:\n${formatHistory(history)}\n\n` +
    `User's new message: ${userMessage}\n\n` +
    `Respond helpfully. Reference specific cards when relevant.`;

  try {
    return await callGemini(prompt);
  } catch {
    return mockResponse('followup', prefs, cards, userMessage);
  }
}

export function isGeminiConfigured(): boolean {
  return Boolean(API_KEY);
}
