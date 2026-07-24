import { GoogleGenerativeAI } from '@google/generative-ai';

export interface SpellCheckRequest {
  text: string;
  language?: string;
  mode?: string;
  customDictionary?: string[];
}

export interface SpellCheckIssue {
  id: string;
  original: string;
  suggestions: string[];
  replacement: string;
  type: string;
  severity: 'error' | 'warning' | 'suggestion';
  confidence: number;
  start: number;
  end: number;
  explanation: string;
  autoFixable: boolean;
}

export interface SpellCheckResponse {
  success: boolean;
  originalText: string;
  correctedText: string;
  summary: {
    totalIssues: number;
    errors: number;
    warnings: number;
    suggestions: number;
    autoFixable: number;
  };
  issues: SpellCheckIssue[];
  aiAssisted?: boolean;
}

const KHMER_RULES: Record<string, { suggestions: string[]; explanation: string; autoFixable: boolean; severity: 'error' | 'warning'; confidence: number }> = {
  'សំរាប់': { suggestions: ['សម្រាប់'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រាប់»។', autoFixable: true, severity: 'error', confidence: 0.96 },
  'សំរេច': { suggestions: ['សម្រេច'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រេច»។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'សំរួល': { suggestions: ['សម្រួល'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រួល»។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'អោយ': { suggestions: ['ឱ្យ'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «ឱ្យ»។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'រឺ': { suggestions: ['ឬ'], explanation: 'សញ្ញាឈ្នាប់ «ឬ» ត្រូវសរសេរដោយប្រើតួអក្សរ ឬ មិនមែន រឺ ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.96 },
  'កំនត់': { suggestions: ['កំណត់'], explanation: 'ពាក្យ «កំណត់» ប្រើប្រកប «ំណ» មិនមែន «ំន» ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'បំនង': { suggestions: ['បំណង'], explanation: 'ពាក្យ «បំណង» ប្រើប្រកប «ំណ» មិនមែន «ំន» ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'តំលៃ': { suggestions: ['តម្លៃ'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «តម្លៃ»។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'តំឡើង': { suggestions: ['ដំឡើង', 'តម្លើង'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «ដំឡើង»។', autoFixable: true, severity: 'warning', confidence: 0.90 },
  'ចំនុច': { suggestions: ['ចំណុច'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «ចំណុច»។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'ចំនែក': { suggestions: ['ចំណែក'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «ចំណែក»។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'ចំនាយ': { suggestions: ['ចំណាយ'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «ចំណាយ»។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'ចំនូល': { suggestions: ['ចំណូល'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «ចំណូល»។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'ប្រពន្ធ័': { suggestions: ['ប្រព័ន្ធ'], explanation: 'ពាក្យ «ប្រព័ន្ធ» ប្រើទណ្ឌឃាតលើ ័ មិនមែន ័ ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.96 },
  'ពិេសស': { suggestions: ['ពិសេស'], explanation: 'ស្រៈ «េ» ត្រូវស្ថិតនៅមុនព្យញ្ជនៈស។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'សម្ភារៈ': { suggestions: ['សម្ភារ'], explanation: 'ពាក្យ «សម្ភារ» មិនត្រូវមាន ៈ នៅខាងចុងឡើយ។', autoFixable: true, severity: 'warning', confidence: 0.92 },
  'អុីនធឺណិត': { suggestions: ['អ៊ីនធឺណិត'], explanation: 'ពាក្យ «អ៊ីនធឺណិត» ត្រូវប្រើស្រៈ អ៊ី មិនមែន អុី ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.95 },
  'សន្តិភព': { suggestions: ['សន្តិភាព'], explanation: 'ពាក្យ «សន្តិភាព» ត្រូវមានស្រៈ ា។', autoFixable: true, severity: 'error', confidence: 0.94 },
};

const EXCLUSION_PATTERNS = [
  /https?:\/\/[^\s]+/gi,
  /www\.[^\s]+/gi,
  /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/gi,
  /\+?\d{8,15}/g,
  /@[a-zA-Z0-9_]{3,}/g,
  /#[a-zA-Z0-9_\u1780-\u17FF]+/g,
  /\/[a-zA-Z0-9_]+/g,
  /```[\s\S]*?```/g,
  /`[^`]+`/g,
  /\{[\s\S]*?\}/g,
  /<[^>]+>/g,
];

export class SpellCheckService {
  private genAI?: GoogleGenerativeAI;

  constructor() {
    const apiKey = process.env.GEMINI_API_KEY;
    if (apiKey && !apiKey.includes('YourGeminiApiKey')) {
      this.genAI = new GoogleGenerativeAI(apiKey);
    }
  }

  public checkSpelling(req: SpellCheckRequest): SpellCheckResponse {
    const text = (req.text || '').substring(0, 5000);
    const customSet = new Set((req.customDictionary || []).map(w => w.trim()));

    const protectedRanges: Array<[number, number]> = [];
    for (const pat of EXCLUSION_PATTERNS) {
      let match: RegExpExecArray | null;
      while ((match = pat.exec(text)) !== null) {
        protectedRanges.push([match.index, match.index + match[0].length]);
      }
    }

    const isProtected = (start: number, end: number) => {
      for (const [pStart, pEnd] of protectedRanges) {
        if (Math.max(start, pStart) < Math.min(end, pEnd)) return true;
      }
      return false;
    };

    const issues: SpellCheckIssue[] = [];
    let issueCount = 1;

    for (const [wordKey, rule] of Object.entries(KHMER_RULES)) {
      if (customSet.has(wordKey)) continue;
      let pos = text.indexOf(wordKey);
      while (pos !== -1) {
        const endPos = pos + wordKey.length;
        if (!isProtected(pos, endPos)) {
          issues.push({
            id: `issue_${issueCount++}`,
            original: wordKey,
            suggestions: rule.suggestions,
            replacement: rule.suggestions[0],
            type: 'spelling',
            severity: rule.severity,
            confidence: rule.confidence,
            start: pos,
            end: endPos,
            explanation: rule.explanation,
            autoFixable: rule.autoFixable && rule.confidence >= 0.90,
          });
        }
        pos = text.indexOf(wordKey, pos + 1);
      }
    }

    // Check double space
    const doubleSpaceRegex = / {2,}/g;
    let dsMatch: RegExpExecArray | null;
    while ((dsMatch = doubleSpaceRegex.exec(text)) !== null) {
      const pos = dsMatch.index;
      const endPos = pos + dsMatch[0].length;
      if (!isProtected(pos, endPos)) {
        issues.push({
          id: `issue_${issueCount++}`,
          original: dsMatch[0],
          suggestions: [' '],
          replacement: ' ',
          type: 'spacing',
          severity: 'warning',
          confidence: 0.98,
          start: pos,
          end: endPos,
          explanation: 'មានចន្លោះច្រើនជាប់គ្នា។ គួរប្រើចន្លោះតែមួយ។',
          autoFixable: true,
        });
      }
    }

    issues.sort((a, b) => a.start - b.start);

    let correctedText = text;
    for (const issue of [...issues].sort((a, b) => b.start - a.start)) {
      if (issue.autoFixable && issue.replacement) {
        correctedText = correctedText.substring(0, issue.start) + issue.replacement + correctedText.substring(issue.end);
      }
    }

    return {
      success: true,
      originalText: text,
      correctedText,
      summary: {
        totalIssues: issues.length,
        errors: issues.filter(i => i.severity === 'error').length,
        warnings: issues.filter(i => i.severity === 'warning').length,
        suggestions: issues.filter(i => i.severity === 'suggestion').length,
        autoFixable: issues.filter(i => i.autoFixable).length,
      },
      issues,
      aiAssisted: false,
    };
  }

  public async checkSpellingAI(req: SpellCheckRequest): Promise<SpellCheckResponse> {
    const baseResult = this.checkSpelling(req);
    const text = (req.text || '').substring(0, 5000);
    if (!text.trim()) return baseResult;

    if (this.genAI) {
      try {
        const modelName = process.env.GEMINI_MODEL || 'gemini-flash-lite-latest';
        const model = this.genAI.getGenerativeModel({ model: modelName });
        const prompt = `You are an expert Khmer Proofreader, Lexicographer, and AI Writing Assistant.
Analyze the following Khmer text for spelling errors, subscript misalignments, spacing mistakes, and phrasing improvements.
Custom dictionary words to ignore: ${JSON.stringify(req.customDictionary || [])}

Text to analyze:
"${text}"

Output STRICTLY a JSON object matching this schema with NO extra text or markdown formatting:
{
  "correctedText": "full corrected text here",
  "issues": [
    {
      "original": "misspelled word",
      "replacement": "correct word",
      "explanation": "Explanation in natural Khmer",
      "severity": "error",
      "autoFixable": true
    }
  ]
}`;
        const result = await model.generateContent(prompt);
        const responseText = result.response.text();
        const jsonMatch = responseText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const aiData = JSON.parse(jsonMatch[0]);
          if (aiData && Array.isArray(aiData.issues)) {
            const mergedIssues = [...baseResult.issues];
            const occupiedSpans = mergedIssues.map(i => [i.start, i.end] as [number, number]);
            let issueCount = mergedIssues.length + 1;
            const customSet = new Set((req.customDictionary || []).map(w => w.trim()));

            for (const aiIssue of aiData.issues) {
              const orig = (aiIssue.original || '').trim();
              const repl = (aiIssue.replacement || '').trim();
              const exp = (aiIssue.explanation || 'ការណែនាំពី Gemini AI').trim();
              const sev = ['error', 'warning', 'suggestion'].includes(aiIssue.severity) ? aiIssue.severity : 'suggestion';

              if (orig && !customSet.has(orig) && text.includes(orig)) {
                let pos = text.indexOf(orig);
                while (pos !== -1) {
                  const endPos = pos + orig.length;
                  const overlaps = occupiedSpans.some(([s, e]) => Math.max(pos, s) < Math.min(endPos, e));
                  if (!overlaps) {
                    mergedIssues.push({
                      id: `issue_ai_${issueCount++}`,
                      original: orig,
                      suggestions: repl ? [repl] : [],
                      replacement: repl,
                      type: sev === 'error' ? 'spelling' : 'ai_grammar',
                      severity: sev as 'error' | 'warning' | 'suggestion',
                      confidence: 0.95,
                      start: pos,
                      end: endPos,
                      explanation: exp,
                      autoFixable: aiIssue.autoFixable !== false,
                    });
                    occupiedSpans.push([pos, endPos]);
                    break;
                  }
                  pos = text.indexOf(orig, pos + 1);
                }
              }
            }

            mergedIssues.sort((a, b) => a.start - b.start);

            let correctedText = text;
            for (const issue of [...mergedIssues].sort((a, b) => b.start - a.start)) {
              if (issue.autoFixable && issue.replacement) {
                correctedText = correctedText.substring(0, issue.start) + issue.replacement + correctedText.substring(issue.end);
              }
            }

            return {
              success: true,
              originalText: text,
              correctedText,
              summary: {
                totalIssues: mergedIssues.length,
                errors: mergedIssues.filter(i => i.severity === 'error').length,
                warnings: mergedIssues.filter(i => i.severity === 'warning').length,
                suggestions: mergedIssues.filter(i => i.severity === 'suggestion').length,
                autoFixable: mergedIssues.filter(i => i.autoFixable).length,
              },
              issues: mergedIssues,
              aiAssisted: true,
            };
          }
        }
      } catch (err) {
        console.warn('TS AI Spell Check fallback to rule-based:', err);
      }
    }

    return baseResult;
  }
}

