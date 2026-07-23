"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MathSolutionResultSchema = exports.QuestionSolutionSchema = exports.SolutionStepSchema = void 0;
const zod_1 = require("zod");
exports.SolutionStepSchema = zod_1.z.object({
    explanation: zod_1.z.string().describe('Explanation of the step in Khmer or English'),
    latex: zod_1.z.string().describe('Valid LaTeX representation of equation or step math'),
});
exports.QuestionSolutionSchema = zod_1.z.object({
    number: zod_1.z.number(),
    original_question: zod_1.z.string().describe('Extracted original text or formula of the problem'),
    question_latex: zod_1.z.string().describe('LaTeX formatted question formula'),
    steps: zod_1.z.array(exports.SolutionStepSchema).min(1),
    final_answer_text: zod_1.z.string().describe('Short text summary of final answer'),
    final_answer_latex: zod_1.z.string().describe('Final answer formatted inside LaTeX e.g. \\boxed{...}'),
});
exports.MathSolutionResultSchema = zod_1.z.object({
    language: zod_1.z.enum(['km', 'en']).default('km'),
    subject: zod_1.z.enum(['mathematics', 'physics', 'chemistry', 'general_science']).default('mathematics'),
    title: zod_1.z.string().default('ដំណោះស្រាយលំហាត់'),
    questions: zod_1.z.array(exports.QuestionSolutionSchema).min(1),
    notes: zod_1.z.array(zod_1.z.string()).default([]),
});
//# sourceMappingURL=math-solution.schema.js.map