import { z } from 'zod';
export type ResponseType = 'mathematics' | 'chemistry' | 'physics' | 'email' | 'document' | 'table' | 'general_image';
export declare const KeyValueSchema: z.ZodObject<{
    label: z.ZodString;
    value: z.ZodString;
}, "strip", z.ZodTypeAny, {
    value: string;
    label: string;
}, {
    value: string;
    label: string;
}>;
export declare const SectionSchema: z.ZodObject<{
    heading: z.ZodString;
    content: z.ZodString;
}, "strip", z.ZodTypeAny, {
    heading: string;
    content: string;
}, {
    heading: string;
    content: string;
}>;
export declare const StructuredSolutionSchema: z.ZodObject<{
    response_type: z.ZodEnum<["mathematics", "chemistry", "physics", "email", "document", "table", "general_image"]>;
    language: z.ZodDefault<z.ZodString>;
    title: z.ZodString;
    summary: z.ZodString;
    sections: z.ZodDefault<z.ZodArray<z.ZodObject<{
        heading: z.ZodString;
        content: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        heading: string;
        content: string;
    }, {
        heading: string;
        content: string;
    }>, "many">>;
    key_values: z.ZodDefault<z.ZodArray<z.ZodObject<{
        label: z.ZodString;
        value: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        value: string;
        label: string;
    }, {
        value: string;
        label: string;
    }>, "many">>;
    warnings: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    recommendations: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    math_expressions: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    language: string;
    title: string;
    response_type: "mathematics" | "physics" | "chemistry" | "email" | "document" | "table" | "general_image";
    summary: string;
    sections: {
        heading: string;
        content: string;
    }[];
    key_values: {
        value: string;
        label: string;
    }[];
    warnings: string[];
    recommendations: string[];
    math_expressions: string[];
}, {
    title: string;
    response_type: "mathematics" | "physics" | "chemistry" | "email" | "document" | "table" | "general_image";
    summary: string;
    language?: string | undefined;
    sections?: {
        heading: string;
        content: string;
    }[] | undefined;
    key_values?: {
        value: string;
        label: string;
    }[] | undefined;
    warnings?: string[] | undefined;
    recommendations?: string[] | undefined;
    math_expressions?: string[] | undefined;
}>;
export type StructuredSolutionResult = z.infer<typeof StructuredSolutionSchema>;
export declare function containsBrokenCharacters(text: string): boolean;
export declare function cleanBrokenCharacters(text: string): string;
