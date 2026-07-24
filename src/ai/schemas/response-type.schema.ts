import { z } from 'zod';

export const ResponseTypeEnum = z.enum([
  'general_answer',
  'code_answer',
  'technical_explanation',
  'software_requirements',
  'project_prototype',
  'system_architecture',
  'database_design',
  'api_design',
  'mathematics',
  'physics',
  'chemistry',
  'email_analysis',
  'document_analysis',
  'table_analysis',
  'general_image_analysis',
  // Backward compatibility aliases
  'email',
  'document',
  'table',
  'general_image'
]);

export type ResponseType = z.infer<typeof ResponseTypeEnum>;

export const KeyValueSchema = z.object({
  label: z.string(),
  value: z.string(),
});

export const SectionSchema = z.object({
  id: z.string().optional(),
  step_number: z.number().optional(),
  type: z.string().optional(),
  heading: z.string().optional(),
  heading_km: z.string().optional(),
  content: z.string().optional(),
  content_km: z.string().optional(),
  items: z.array(z.any()).optional(),
  tables: z.array(z.any()).optional(),
  endpoints: z.array(z.any()).optional(),
  language: z.string().optional(),
  filename: z.string().optional(),
  code: z.string().optional(),
});

export const StructuredSolutionSchema = z.object({
  response_type: ResponseTypeEnum,
  language: z.string().default('km'),
  title: z.string(),
  subtitle: z.string().optional(),
  summary: z.string().optional(),
  summary_km: z.string().optional(),
  tags: z.array(z.string()).default([]),
  sections: z.array(SectionSchema).default([]),
  key_values: z.array(KeyValueSchema).default([]),
  warnings: z.array(z.string()).default([]),
  recommendations: z.array(z.string()).default([]),
  math_expressions: z.array(z.string()).default([]),
  suggested_actions: z.array(z.string()).default([]),
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
