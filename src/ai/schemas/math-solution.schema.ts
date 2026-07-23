import { z } from 'zod';

export const SolutionStepSchema = z.object({
  explanation: z.string().describe('Explanation of the step in Khmer or English'),
  latex: z.string().describe('Valid LaTeX representation of equation or step math'),
});

export const QuestionSolutionSchema = z.object({
  number: z.number(),
  original_question: z.string().describe('Extracted original text or formula of the problem'),
  question_latex: z.string().describe('LaTeX formatted question formula'),
  steps: z.array(SolutionStepSchema).min(1),
  final_answer_text: z.string().describe('Short text summary of final answer'),
  final_answer_latex: z.string().describe('Final answer formatted inside LaTeX e.g. \\boxed{...}'),
});

export const MathSolutionResultSchema = z.object({
  language: z.enum(['km', 'en']).default('km'),
  subject: z.enum(['mathematics', 'physics', 'chemistry', 'general_science']).default('mathematics'),
  title: z.string().default('ដំណោះស្រាយលំហាត់'),
  questions: z.array(QuestionSolutionSchema).min(1),
  notes: z.array(z.string()).default([]),
});

export type SolutionStep = z.infer<typeof SolutionStepSchema>;
export type QuestionSolution = z.infer<typeof QuestionSolutionSchema>;
export type MathSolutionResult = z.infer<typeof MathSolutionResultSchema>;
