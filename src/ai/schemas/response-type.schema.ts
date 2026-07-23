import { z } from 'zod';

export type ResponseType =
  | 'mathematics'
  | 'chemistry'
  | 'physics'
  | 'email'
  | 'document'
  | 'table'
  | 'general_image';

export const KeyValueSchema = z.object({
  label: z.string(),
  value: z.string(),
});

export const SectionSchema = z.object({
  heading: z.string(),
  content: z.string(),
});

export const StructuredSolutionSchema = z.object({
  response_type: z.enum([
    'mathematics',
    'chemistry',
    'physics',
    'email',
    'document',
    'table',
    'general_image',
  ]),
  language: z.string().default('km'),
  title: z.string(),
  summary: z.string(),
  sections: z.array(SectionSchema).default([]),
  key_values: z.array(KeyValueSchema).default([]),
  warnings: z.array(z.string()).default([]),
  recommendations: z.array(z.string()).default([]),
  math_expressions: z.array(z.string()).default([]),
});

export type StructuredSolutionResult = z.infer<typeof StructuredSolutionSchema>;

export function containsBrokenCharacters(text: string): boolean {
  if (!text) return false;
  const brokenPatterns = ['\u25A1', '\uFFFD', '\u25A0', '\u25A2', '\u25A3'];
  return brokenPatterns.some((pattern) => text.includes(pattern));
}

export function cleanBrokenCharacters(text: string): string {
  if (!text) return '';
  let cleaned = text.normalize('NFC');
  cleaned = cleaned.replace(/[\u25A1\u25A0\u25A2\u25A3\u25A4\u25A5]/g, '•');
  cleaned = cleaned.replace(/\uFFFD/g, '');
  cleaned = cleaned.replace(/•\s*•+/g, '•');
  return cleaned.trim();
}
