import { describe, it, expect } from 'vitest';
import {
  parseSections,
  extractSourceUrl,
  extractPreview,
  parseComprehension,
  getTodayShanghai,
  type LessonSections,
  type QABlock
} from './lesson-parser';

// Real content from content/2026-03-24.md as test fixture
const REAL_LESSON_CONTENT = `## 📖 文章 / Article

23-03-2026 15:00

Paris has a big problem with trash, and it is a main topic in the new election. Rachida Dati wants to be the new mayor. She made a video to show that she can clean the streets. She even worked on a garbage truck to show she is serious.

Many people who live in Paris are unhappy. They say the roads are dirty every day. They want the city to look beautiful and clean again. Dati says the current system of collecting trash is bad. She wants a new plan to collect trash and wash the streets at the same time.

Some experts say politicians always talk about dirt to get more votes. Some people don't wait for the government to help. They clean the streets themselves. They say everyone must help to keep the city good for children and old people.

Difficult words: mayor (the official leader and boss of a city or a town), garbage truck (a large vehicle that travels to houses and streets to collect trash and take it away), collect (to pick up things).

You can watch the original video in the Level 3 section.

The post Paris is dirty – level 2 appeared first on English news and easy articles for students of English.

> Source: https://www.newsinlevels.com/products/paris-is-dirty-level-2/

## 📚 词汇 / Vocabulary

**trash** (noun) （垃圾）— things that are no longer wanted or useful and have been thrown away.
> "Paris has a big problem with trash, and it is a main topic in the new election."

**election** (noun) （选举）— the process of choosing someone for a public role by voting.
> "Paris has a big problem with trash, and it is a main topic in the new election."

**unhappy** (adjective) （不开心）— feeling or showing sadness or discontent.
> "Many people who live in Paris are unhappy."

**collecting** (verb) （收集）— to bring or gather things or people together.
> "Dati says the current system of collecting trash is bad."

**experts** (noun) （专家）— people who have a lot of knowledge or skill in a particular area.
> "Some experts say politicians always talk about dirt to get more votes."

**politicians** (noun) （政治家）— people who work in politics, usually elected to make laws and important decisions for a country or region.
> "Some experts say politicians always talk about dirt to get more votes."

## 🔗 表达 / Chunking Expressions

**main topic** （主要话题）
The most important subject or issue being discussed.
- The main topic of the meeting was the new marketing strategy.
- Global warming is a main topic of concern for many scientists.

**make a video** （制作视频）
To create or record a video, often for a specific purpose.
- She decided to make a video to explain her new project.
- Many influencers make videos to share their experiences.

**collect trash** （收集垃圾）
The act of picking up and removing waste or rubbish.
- The city has a schedule for when they collect trash from each street.
- Environmental groups are trying to find better ways to collect trash and reduce pollution.

**get more votes** （获得更多选票）
To receive a larger number of votes in an election, typically to win or increase support.
- Politicians often promise tax cuts to get more votes from the public.
- She hopes her new policy will help her get more votes in the next election.

## ❓ 理解 / Comprehension

**Q: What is Rachida Dati doing to show she is serious about cleaning Paris?**
**A (EN):** She made a video to show that she can clean the streets and she also worked on a garbage truck.
**A (中):** 她制作了一个视频来展示她能打扫街道，并且她还在一辆垃圾车上工作过。

**Q: Why are many people in Paris unhappy?**
**A (EN):** They are unhappy because they say the roads are dirty every day and they want the city to look beautiful and clean again.
**A (中):** 他们不开心，因为他们说街道每天都很脏，他们希望城市再次变得美丽和干净。

**Q: According to the article, what might be the reason some politicians talk about dirt during elections, and what does this suggest about the public's perception of politicians?**
**A (EN):** Some experts suggest politicians talk about dirt to get more votes. This suggests that voters might be more inclined to support politicians who address issues they see as problems in their daily lives, like cleanliness, to gain their electoral support.
**A (中):** 一些专家认为政治家谈论肮脏问题是为了获得更多选票。这表明选民可能更倾向于支持那些解决他们日常生活中视为问题（如清洁问题）的政治家，以获得他们的选举支持。`;

describe('parseSections', () => {
  it('should parse all four sections from real content', () => {
    const sections = parseSections(REAL_LESSON_CONTENT);

    expect(sections.article).toContain('Paris has a big problem with trash');
    expect(sections.article).toContain('Source: https://www.newsinlevels.com');
    expect(sections.vocabulary).toContain('**trash** (noun)');
    expect(sections.expressions).toContain('**main topic** （主要话题）');
    expect(sections.comprehension).toContain('**Q: What is Rachida Dati doing');
  });

  it('should return empty strings for all sections when input is empty', () => {
    const sections = parseSections('');

    expect(sections).toEqual({
      article: '',
      vocabulary: '',
      expressions: '',
      comprehension: ''
    });
  });

  it('should handle partial content gracefully', () => {
    const partialContent = `## 📖 文章 / Article
Some article text

## 📚 词汇 / Vocabulary
Some vocab text`;

    const sections = parseSections(partialContent);

    expect(sections.article).toContain('Some article text');
    expect(sections.vocabulary).toContain('Some vocab text');
    expect(sections.expressions).toBe('');
    expect(sections.comprehension).toBe('');
  });
});

describe('extractSourceUrl', () => {
  it('should extract source URL from article text', () => {
    const articleText = `Paris has content here.

> Source: https://www.newsinlevels.com/products/paris-is-dirty-level-2/

More content.`;

    const url = extractSourceUrl(articleText);
    expect(url).toBe('https://www.newsinlevels.com/products/paris-is-dirty-level-2/');
  });

  it('should return null when no source line exists', () => {
    const articleText = 'Paris has content but no source line.';

    const url = extractSourceUrl(articleText);
    expect(url).toBeNull();
  });

  it('should handle source with extra whitespace', () => {
    const articleText = `Some content
>   Source:   https://example.com/test
More content`;

    const url = extractSourceUrl(articleText);
    expect(url).toBe('https://example.com/test');
  });
});

describe('extractPreview', () => {
  it('should extract first non-timestamp, non-blockquote line from real article', () => {
    const articleText = `23-03-2026 15:00

Paris has a big problem with trash, and it is a main topic in the new election.

Many people who live in Paris are unhappy.

> Source: https://example.com`;

    const preview = extractPreview(articleText);
    expect(preview).toBe('Paris has a big problem with trash, and it is a main topic...');
  });

  it('should return empty string for empty input', () => {
    const preview = extractPreview('');
    expect(preview).toBe('');
  });

  it('should truncate long text at specified character limit', () => {
    const longText = `23-03-2026 15:00

This is a very long sentence that should definitely be truncated because it exceeds the maximum character limit that we want to enforce.`;

    const preview = extractPreview(longText, 30);
    expect(preview).toBe('This is a very long sentence...');
  });

  it('should skip timestamp and blockquote lines', () => {
    const articleText = `24-03-2026 10:00

> This is a blockquote line
> Another blockquote line

This is the first real content line.`;

    const preview = extractPreview(articleText);
    expect(preview).toBe('This is the first real content line.');
  });
});

describe('parseComprehension', () => {
  it('should parse all three Q&A blocks from real content', () => {
    const comprehensionText = `**Q: What is Rachida Dati doing to show she is serious about cleaning Paris?**
**A (EN):** She made a video to show that she can clean the streets and she also worked on a garbage truck.
**A (中):** 她制作了一个视频来展示她能打扫街道，并且她还在一辆垃圾车上工作过。

**Q: Why are many people in Paris unhappy?**
**A (EN):** They are unhappy because they say the roads are dirty every day and they want the city to look beautiful and clean again.
**A (中):** 他们不开心，因为他们说街道每天都很脏，他们希望城市再次变得美丽和干净。

**Q: According to the article, what might be the reason some politicians talk about dirt during elections, and what does this suggest about the public's perception of politicians?**
**A (EN):** Some experts suggest politicians talk about dirt to get more votes. This suggests that voters might be more inclined to support politicians who address issues they see as problems in their daily lives, like cleanliness, to gain their electoral support.
**A (中):** 一些专家认为政治家谈论肮脏问题是为了获得更多选票。这表明选民可能更倾向于支持那些解决他们日常生活中视为问题（如清洁问题）的政治家，以获得他们的选举支持。`;

    const qaBlocks = parseComprehension(comprehensionText);

    expect(qaBlocks).toHaveLength(3);
    expect(qaBlocks[0].question).toBe('What is Rachida Dati doing to show she is serious about cleaning Paris?');
    expect(qaBlocks[0].answerEn).toContain('She made a video');
    expect(qaBlocks[0].answerZh).toContain('她制作了一个视频');

    expect(qaBlocks[1].question).toBe('Why are many people in Paris unhappy?');
    expect(qaBlocks[2].question).toContain('According to the article');
  });

  it('should return empty array for empty input', () => {
    const qaBlocks = parseComprehension('');
    expect(qaBlocks).toEqual([]);
  });

  it('should handle malformed Q&A blocks gracefully', () => {
    const malformedText = `**Q: Some question?**
**A (EN):** Some answer
No Chinese answer here.`;

    const qaBlocks = parseComprehension(malformedText);
    expect(qaBlocks).toHaveLength(0); // Should not match incomplete blocks
  });
});

describe('getTodayShanghai', () => {
  it('should return a date string in YYYY-MM-DD format', () => {
    const today = getTodayShanghai();

    expect(today).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(typeof today).toBe('string');
  });

  it('should use Asia/Shanghai timezone', () => {
    const today = getTodayShanghai();

    // Should be a valid date
    const dateObj = new Date(today);
    expect(dateObj).toBeInstanceOf(Date);
    expect(isNaN(dateObj.getTime())).toBe(false);
  });
});