export interface LessonSections {
  article: string;
  vocabulary: string;
  expressions: string;
  comprehension: string;
}

export interface QABlock {
  question: string;
  answerEn: string;
  answerZh: string;
}

export function parseSections(body: string): LessonSections {
  if (!body.trim()) {
    return {
      article: '',
      vocabulary: '',
      expressions: '',
      comprehension: ''
    };
  }

  // Split on section headers using regex
  const sections: LessonSections = {
    article: '',
    vocabulary: '',
    expressions: '',
    comprehension: ''
  };

  // Match section headers and capture content
  const articleMatch = body.match(/## 📖 文章 \/ Article\s*([\s\S]*?)(?=## 📚|$)/);
  const vocabularyMatch = body.match(/## 📚 词汇 \/ Vocabulary\s*([\s\S]*?)(?=## 🔗|$)/);
  const expressionsMatch = body.match(/## 🔗 表达 \/ Chunking Expressions\s*([\s\S]*?)(?=## ❓|$)/);
  const comprehensionMatch = body.match(/## ❓ 理解 \/ Comprehension\s*([\s\S]*)$/);

  sections.article = articleMatch ? articleMatch[1].trim() : '';
  sections.vocabulary = vocabularyMatch ? vocabularyMatch[1].trim() : '';
  sections.expressions = expressionsMatch ? expressionsMatch[1].trim() : '';
  sections.comprehension = comprehensionMatch ? comprehensionMatch[1].trim() : '';

  return sections;
}

export function extractSourceUrl(articleText: string): string | null {
  const match = articleText.match(/^>\s*Source:\s*(https?:\/\/\S+)/m);
  return match ? match[1] : null;
}

export function extractPreview(articleText: string, maxChars = 60): string {
  if (!articleText.trim()) {
    return '';
  }

  // Split into lines and filter
  const lines = articleText.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0)
    .filter(line => !line.match(/^\d{2}-\d{2}-\d{4}/)) // Skip timestamp format
    .filter(line => !line.startsWith('>')); // Skip blockquote lines

  if (lines.length === 0) {
    return '';
  }

  const firstLine = lines[0];
  if (firstLine.length <= maxChars) {
    return firstLine;
  }

  // Split into words and find how many fit within maxChars
  const words = firstLine.split(' ');
  let result = '';

  for (let i = 0; i < words.length; i++) {
    const testString = result + (result ? ' ' : '') + words[i];
    if (testString.length <= maxChars) {
      result = testString;
    } else {
      break;
    }
  }

  return result + '...';
}

export function parseComprehension(text: string): QABlock[] {
  if (!text.trim()) {
    return [];
  }

  const qaBlocks: QABlock[] = [];

  // Use regex with global and dotall flags to match Q&A blocks
  const pattern = /\*\*Q:\s*(.*?)\*\*\s*\n\*\*A \(EN\):\*\*\s*([\s\S]*?)\n\*\*A \(中\):\*\*\s*([\s\S]*?)(?=\n\*\*Q:|$)/g;

  let match;
  while ((match = pattern.exec(text)) !== null) {
    qaBlocks.push({
      question: match[1].trim(),
      answerEn: match[2].trim(),
      answerZh: match[3].trim()
    });
  }

  return qaBlocks;
}

// Common English function words — unstressed in normal speech
const FUNCTION_WORDS = new Set([
  // Articles
  'a', 'an', 'the',
  // Personal pronouns
  'i', 'you', 'he', 'she', 'it', 'we', 'they',
  'me', 'him', 'her', 'us', 'them',
  // Possessives
  'my', 'your', 'his', 'its', 'our', 'their',
  'mine', 'yours', 'hers', 'ours', 'theirs',
  // Demonstratives
  'this', 'that', 'these', 'those',
  // Relatives / interrogatives
  'who', 'whom', 'which', 'whose',
  // Prepositions
  'in', 'on', 'at', 'by', 'for', 'of', 'to', 'from', 'with', 'about',
  'as', 'than', 'like', 'after', 'before', 'since', 'until',
  'up', 'down', 'out', 'off', 'over', 'under', 'into', 'onto',
  'through', 'across', 'against', 'along', 'among', 'around',
  'behind', 'below', 'beside', 'between', 'despite', 'except',
  'inside', 'near', 'outside', 'toward', 'within', 'without',
  // Conjunctions
  'and', 'but', 'or', 'nor', 'so', 'yet',
  'because', 'although', 'though', 'while', 'if', 'when', 'where',
  'whether', 'unless', 'whereas',
  // Auxiliary verbs
  'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
  'have', 'has', 'had', 'having',
  'will', 'would', 'shall', 'should',
  'may', 'might', 'must', 'can', 'could',
  'do', 'does', 'did',
  // Common unstressed adverbs/particles
  'not', 'very', 'just', 'only', 'also', 'too', 'even',
  'there', 'here', 'then', 'still', 'already', 'again',
  // Quantifiers (function-like)
  'some', 'any', 'all', 'both', 'each', 'either', 'neither',
  'more', 'most', 'much', 'many', 'few', 'less', 'enough', 'other', 'another',
  // Misc
  'no', 'well', 'such',
]);

type TokenType = 'word' | 'space' | 'punct';
interface Token { type: TokenType; value: string; }

function tokenize(text: string): Token[] {
  const tokens: Token[] = [];
  const re = /([a-zA-Z'']+)|(\s+)|([^a-zA-Z''\s])/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    if (m[1]) tokens.push({ type: 'word', value: m[1] });
    else if (m[2]) tokens.push({ type: 'space', value: m[2] });
    else tokens.push({ type: 'punct', value: m[3] });
  }
  return tokens;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Subordinating conjunctions that mark clause boundaries (pause before them)
const CLAUSE_STARTERS = new Set([
  'because', 'although', 'though', 'even though',
  'while', 'when', 'whenever', 'where', 'wherever',
  'if', 'unless', 'until', 'since', 'as',
  'which', 'that', 'who', 'whom', 'whose',
  'before', 'after', 'once', 'whereas', 'whether',
]);

/**
 * Annotate an English paragraph with:
 *  - Linking:    consonant→vowel word boundary → .linked-words
 *  - Stress:     nuclear accent per clause     → .word-nuclear (ˈ above)
 *  - Intonation: sentence-end tone arrows      → .tone-fall / .tone-rise
 *  - Pauses:     comma minor pause             → .pause-minor  (·)
 *                clause-starter boundary       → .pause-clause (｜)
 * Returns HTML safe to render with set:html.
 */
export function annotateArticle(text: string): string {
  if (!text) return '';

  const CONSONANTS = new Set('bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ');
  const VOWELS     = new Set('aeiouAEIOU');

  const tokens = tokenize(text);

  // ── Pass 1: classify words ─────────────────────────────────
  // 'content' | 'func' — only for word tokens
  const wordClass = new Map<number, 'content' | 'func'>();
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i].type !== 'word') continue;
    const w = tokens[i].value.toLowerCase().replace(/['']/g, "'");
    wordClass.set(i, FUNCTION_WORDS.has(w) ? 'func' : 'content');
  }

  // ── Pass 2: find nuclear accent per clause ─────────────────
  // Nuclear = last content word before a clause-ending punct
  const isNuclear = new Set<number>();
  const clausePunct = new Set(['.', '!', '?', ',', ';', ':', '—', '–']);

  let clauseContentIdx: number[] = [];
  const flushClause = () => {
    let last = -1;
    for (const idx of clauseContentIdx) {
      if (wordClass.get(idx) === 'content') last = idx;
    }
    if (last >= 0) isNuclear.add(last);
    clauseContentIdx = [];
  };

  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.type === 'word') clauseContentIdx.push(i);
    else if (t.type === 'punct' && clausePunct.has(t.value)) flushClause();
  }
  flushClause();

  // ── Pass 3: build HTML ─────────────────────────────────────
  const sentenceEndPunct = new Set(['.', '!', '?']);

  const renderWord = (i: number): string => {
    const raw = escapeHtml(tokens[i].value);
    if (isNuclear.has(i)) return `<span class="word-nuclear">${raw}</span>`;
    if (wordClass.get(i) === 'func') return `<span class="word-func">${raw}</span>`;
    return raw; // content words need no extra span
  };

  let out = '';
  let i = 0;

  while (i < tokens.length) {
    const t = tokens[i];

    if (t.type === 'word') {
      const wLower = t.value.toLowerCase();

      // Insert clause-boundary pause before subordinating conjunctions
      // (skip if this is the very first token)
      if (CLAUSE_STARTERS.has(wLower) && out.trim().length > 0) {
        out += '<span class="pause-clause">｜</span>';
      }

      // Check consonant→vowel linking with next word
      const lastChar = t.value[t.value.length - 1];
      if (CONSONANTS.has(lastChar)) {
        let j = i + 1;
        while (j < tokens.length && tokens[j].type === 'space') j++;
        if (
          j < tokens.length &&
          tokens[j].type === 'word' &&
          VOWELS.has(tokens[j].value[0])
        ) {
          const spaceBetween = tokens
            .slice(i + 1, j)
            .map(tk => tk.value)
            .join('');
          out += `<span class="linked-words">${renderWord(i)}${spaceBetween}${renderWord(j)}</span>`;
          i = j + 1;
          continue;
        }
      }
      out += renderWord(i);
      i++;

    } else if (t.type === 'space') {
      out += t.value;
      i++;

    } else {
      // Punctuation
      out += escapeHtml(t.value);
      // Minor pause dot after comma / semicolon
      if (t.value === ',' || t.value === ';') {
        out += '<span class="pause-minor">·</span>';
      }
      if (sentenceEndPunct.has(t.value)) {
        const isMaybeQuestion = t.value === '?';
        out += isMaybeQuestion
          ? '<span class="tone-rise">↗</span>'
          : '<span class="tone-fall">↘</span>';
      }
      i++;
    }
  }

  return out;
}

/** @deprecated Use annotateArticle instead */
export function annotateLinking(text: string): string {
  return annotateArticle(text);
}

export function getTodayShanghai(): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(new Date());
}