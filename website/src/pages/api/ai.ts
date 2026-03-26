import type { APIRoute } from 'astro';
import { GoogleGenAI } from '@google/genai';

export const prerender = false;

const MODEL = 'gemini-2.5-flash-lite';

interface ChatMessage {
  role: 'user' | 'model';
  text: string;
}

interface RequestBody {
  action: 'chat' | 'analyze' | 'practice_prompt' | 'practice_feedback';
  articleContent?: string;
  vocabWords?: string[];
  message?: string;
  history?: ChatMessage[];
  selection?: string;
  practicePrompt?: string;
  userResponse?: string;
}

export const POST: APIRoute = async ({ request }) => {
  const apiKey = import.meta.env.GEMINI_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'AI service not configured' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  let body: RequestBody;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid request body' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const ai = new GoogleGenAI({ apiKey });

  try {
    let content = '';

    if (body.action === 'chat') {
      const systemContext = body.articleContent
        ? `You are an English learning assistant. The student is reading this article:\n\n---\n${body.articleContent}\n---\n\nAnswer questions about the article concisely. Use Chinese (中文) for explanations unless the student writes in English. Keep responses brief and helpful.`
        : 'You are a helpful English learning assistant. Answer in Chinese unless the student writes in English. Keep responses brief.';

      const history = (body.history ?? []).map(m => ({
        role: m.role as 'user' | 'model',
        parts: [{ text: m.text }],
      }));

      const chat = ai.chats.create({
        model: MODEL,
        config: { systemInstruction: systemContext },
        history,
      });

      const response = await chat.sendMessage({
        message: body.message ?? '',
      });
      content = response.text ?? '';

    } else if (body.action === 'analyze') {
      const articleCtx = body.articleContent
        ? `\n\nArticle context:\n${body.articleContent.slice(0, 2000)}`
        : '';
      const prompt = `You are an English learning assistant. Analyze the following selected text for an English learner:\n\n"${body.selection}"${articleCtx}\n\nProvide a concise analysis in Chinese covering:\n1. 词义/用法 (meaning and usage)\n2. 语法结构 (grammar if it's a phrase/sentence)\n3. 朗读提示 (pronunciation tip if relevant)\n\nKeep it brief, under 150 words.`;

      const response = await ai.models.generateContent({
        model: MODEL,
        contents: prompt,
      });
      content = response.text ?? '';

    } else if (body.action === 'practice_prompt') {
      const vocab = body.vocabWords?.slice(0, 5).join(', ') ?? '';
      const articleCtx = body.articleContent
        ? body.articleContent.slice(0, 1000)
        : '';
      const prompt = `You are an English writing coach. Based on this English learning article context:\n\n"${articleCtx}"\n\nKey vocabulary: ${vocab}\n\nGenerate a short writing practice prompt in Chinese (1-2 sentences) that:\n- Asks the student to write 2-3 sentences in English\n- Encourages using the vocabulary from the article\n- Is interesting and relevant to the article topic\n\nOnly output the prompt itself, nothing else.`;

      const response = await ai.models.generateContent({
        model: MODEL,
        contents: prompt,
      });
      content = response.text ?? '';

    } else if (body.action === 'practice_feedback') {
      const prompt = `You are a helpful English writing coach. The student was given this practice prompt:\n\n"${body.practicePrompt}"\n\nThe student wrote:\n\n"${body.userResponse}"\n\nProvide brief, encouraging feedback in Chinese (under 120 words) covering:\n1. ✅ 做得好的地方\n2. 📝 1-2个改进建议（具体的语法或表达）\n3. 给出一个改写示例句`;

      const response = await ai.models.generateContent({
        model: MODEL,
        contents: prompt,
      });
      content = response.text ?? '';

    } else {
      return new Response(JSON.stringify({ error: 'Unknown action' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({ content }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'AI request failed';
    return new Response(JSON.stringify({ error: message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
