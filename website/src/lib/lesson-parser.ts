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

export function getTodayShanghai(): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(new Date());
}