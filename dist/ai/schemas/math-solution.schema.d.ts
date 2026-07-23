import { z } from 'zod';
export declare const SolutionStepSchema: z.ZodObject<{
    explanation: z.ZodString;
    latex: z.ZodString;
}, "strip", z.ZodTypeAny, {
    explanation: string;
    latex: string;
}, {
    explanation: string;
    latex: string;
}>;
export declare const QuestionSolutionSchema: z.ZodObject<{
    number: z.ZodNumber;
    original_question: z.ZodString;
    question_latex: z.ZodString;
    steps: z.ZodArray<z.ZodObject<{
        explanation: z.ZodString;
        latex: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        explanation: string;
        latex: string;
    }, {
        explanation: string;
        latex: string;
    }>, "many">;
    final_answer_text: z.ZodString;
    final_answer_latex: z.ZodString;
}, "strip", z.ZodTypeAny, {
    number: number;
    original_question: string;
    question_latex: string;
    steps: {
        explanation: string;
        latex: string;
    }[];
    final_answer_text: string;
    final_answer_latex: string;
}, {
    number: number;
    original_question: string;
    question_latex: string;
    steps: {
        explanation: string;
        latex: string;
    }[];
    final_answer_text: string;
    final_answer_latex: string;
}>;
export declare const MathSolutionResultSchema: z.ZodObject<{
    language: z.ZodDefault<z.ZodEnum<["km", "en"]>>;
    subject: z.ZodDefault<z.ZodEnum<["mathematics", "physics", "chemistry", "general_science"]>>;
    title: z.ZodDefault<z.ZodString>;
    questions: z.ZodArray<z.ZodObject<{
        number: z.ZodNumber;
        original_question: z.ZodString;
        question_latex: z.ZodString;
        steps: z.ZodArray<z.ZodObject<{
            explanation: z.ZodString;
            latex: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            explanation: string;
            latex: string;
        }, {
            explanation: string;
            latex: string;
        }>, "many">;
        final_answer_text: z.ZodString;
        final_answer_latex: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        number: number;
        original_question: string;
        question_latex: string;
        steps: {
            explanation: string;
            latex: string;
        }[];
        final_answer_text: string;
        final_answer_latex: string;
    }, {
        number: number;
        original_question: string;
        question_latex: string;
        steps: {
            explanation: string;
            latex: string;
        }[];
        final_answer_text: string;
        final_answer_latex: string;
    }>, "many">;
    notes: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    language: "km" | "en";
    subject: "mathematics" | "physics" | "chemistry" | "general_science";
    title: string;
    questions: {
        number: number;
        original_question: string;
        question_latex: string;
        steps: {
            explanation: string;
            latex: string;
        }[];
        final_answer_text: string;
        final_answer_latex: string;
    }[];
    notes: string[];
}, {
    questions: {
        number: number;
        original_question: string;
        question_latex: string;
        steps: {
            explanation: string;
            latex: string;
        }[];
        final_answer_text: string;
        final_answer_latex: string;
    }[];
    language?: "km" | "en" | undefined;
    subject?: "mathematics" | "physics" | "chemistry" | "general_science" | undefined;
    title?: string | undefined;
    notes?: string[] | undefined;
}>;
export type SolutionStep = z.infer<typeof SolutionStepSchema>;
export type QuestionSolution = z.infer<typeof QuestionSolutionSchema>;
export type MathSolutionResult = z.infer<typeof MathSolutionResultSchema>;
