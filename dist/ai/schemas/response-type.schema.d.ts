import { z } from 'zod';
export declare const ResponseTypeEnum: z.ZodEnum<["general_answer", "code_answer", "technical_explanation", "software_requirements", "project_prototype", "system_architecture", "database_design", "api_design", "mathematics", "physics", "chemistry", "email_analysis", "document_analysis", "table_analysis", "general_image_analysis", "email", "document", "table", "general_image"]>;
export type ResponseType = z.infer<typeof ResponseTypeEnum>;
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
    id: z.ZodOptional<z.ZodString>;
    step_number: z.ZodOptional<z.ZodNumber>;
    type: z.ZodOptional<z.ZodString>;
    heading: z.ZodOptional<z.ZodString>;
    heading_km: z.ZodOptional<z.ZodString>;
    content: z.ZodOptional<z.ZodString>;
    content_km: z.ZodOptional<z.ZodString>;
    items: z.ZodOptional<z.ZodArray<z.ZodAny, "many">>;
    tables: z.ZodOptional<z.ZodArray<z.ZodAny, "many">>;
    endpoints: z.ZodOptional<z.ZodArray<z.ZodAny, "many">>;
    language: z.ZodOptional<z.ZodString>;
    filename: z.ZodOptional<z.ZodString>;
    code: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    code?: string | undefined;
    type?: string | undefined;
    id?: string | undefined;
    language?: string | undefined;
    step_number?: number | undefined;
    heading?: string | undefined;
    heading_km?: string | undefined;
    content?: string | undefined;
    content_km?: string | undefined;
    items?: any[] | undefined;
    tables?: any[] | undefined;
    endpoints?: any[] | undefined;
    filename?: string | undefined;
}, {
    code?: string | undefined;
    type?: string | undefined;
    id?: string | undefined;
    language?: string | undefined;
    step_number?: number | undefined;
    heading?: string | undefined;
    heading_km?: string | undefined;
    content?: string | undefined;
    content_km?: string | undefined;
    items?: any[] | undefined;
    tables?: any[] | undefined;
    endpoints?: any[] | undefined;
    filename?: string | undefined;
}>;
export declare const StructuredSolutionSchema: z.ZodObject<{
    response_type: z.ZodEnum<["general_answer", "code_answer", "technical_explanation", "software_requirements", "project_prototype", "system_architecture", "database_design", "api_design", "mathematics", "physics", "chemistry", "email_analysis", "document_analysis", "table_analysis", "general_image_analysis", "email", "document", "table", "general_image"]>;
    language: z.ZodDefault<z.ZodString>;
    title: z.ZodString;
    subtitle: z.ZodOptional<z.ZodString>;
    summary: z.ZodOptional<z.ZodString>;
    summary_km: z.ZodOptional<z.ZodString>;
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    sections: z.ZodDefault<z.ZodArray<z.ZodObject<{
        id: z.ZodOptional<z.ZodString>;
        step_number: z.ZodOptional<z.ZodNumber>;
        type: z.ZodOptional<z.ZodString>;
        heading: z.ZodOptional<z.ZodString>;
        heading_km: z.ZodOptional<z.ZodString>;
        content: z.ZodOptional<z.ZodString>;
        content_km: z.ZodOptional<z.ZodString>;
        items: z.ZodOptional<z.ZodArray<z.ZodAny, "many">>;
        tables: z.ZodOptional<z.ZodArray<z.ZodAny, "many">>;
        endpoints: z.ZodOptional<z.ZodArray<z.ZodAny, "many">>;
        language: z.ZodOptional<z.ZodString>;
        filename: z.ZodOptional<z.ZodString>;
        code: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        code?: string | undefined;
        type?: string | undefined;
        id?: string | undefined;
        language?: string | undefined;
        step_number?: number | undefined;
        heading?: string | undefined;
        heading_km?: string | undefined;
        content?: string | undefined;
        content_km?: string | undefined;
        items?: any[] | undefined;
        tables?: any[] | undefined;
        endpoints?: any[] | undefined;
        filename?: string | undefined;
    }, {
        code?: string | undefined;
        type?: string | undefined;
        id?: string | undefined;
        language?: string | undefined;
        step_number?: number | undefined;
        heading?: string | undefined;
        heading_km?: string | undefined;
        content?: string | undefined;
        content_km?: string | undefined;
        items?: any[] | undefined;
        tables?: any[] | undefined;
        endpoints?: any[] | undefined;
        filename?: string | undefined;
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
    suggested_actions: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    language: string;
    title: string;
    response_type: "mathematics" | "physics" | "chemistry" | "general_answer" | "code_answer" | "technical_explanation" | "software_requirements" | "project_prototype" | "system_architecture" | "database_design" | "api_design" | "email_analysis" | "document_analysis" | "table_analysis" | "general_image_analysis" | "email" | "document" | "table" | "general_image";
    tags: string[];
    sections: {
        code?: string | undefined;
        type?: string | undefined;
        id?: string | undefined;
        language?: string | undefined;
        step_number?: number | undefined;
        heading?: string | undefined;
        heading_km?: string | undefined;
        content?: string | undefined;
        content_km?: string | undefined;
        items?: any[] | undefined;
        tables?: any[] | undefined;
        endpoints?: any[] | undefined;
        filename?: string | undefined;
    }[];
    key_values: {
        value: string;
        label: string;
    }[];
    warnings: string[];
    recommendations: string[];
    math_expressions: string[];
    suggested_actions: string[];
    subtitle?: string | undefined;
    summary?: string | undefined;
    summary_km?: string | undefined;
}, {
    title: string;
    response_type: "mathematics" | "physics" | "chemistry" | "general_answer" | "code_answer" | "technical_explanation" | "software_requirements" | "project_prototype" | "system_architecture" | "database_design" | "api_design" | "email_analysis" | "document_analysis" | "table_analysis" | "general_image_analysis" | "email" | "document" | "table" | "general_image";
    language?: string | undefined;
    subtitle?: string | undefined;
    summary?: string | undefined;
    summary_km?: string | undefined;
    tags?: string[] | undefined;
    sections?: {
        code?: string | undefined;
        type?: string | undefined;
        id?: string | undefined;
        language?: string | undefined;
        step_number?: number | undefined;
        heading?: string | undefined;
        heading_km?: string | undefined;
        content?: string | undefined;
        content_km?: string | undefined;
        items?: any[] | undefined;
        tables?: any[] | undefined;
        endpoints?: any[] | undefined;
        filename?: string | undefined;
    }[] | undefined;
    key_values?: {
        value: string;
        label: string;
    }[] | undefined;
    warnings?: string[] | undefined;
    recommendations?: string[] | undefined;
    math_expressions?: string[] | undefined;
    suggested_actions?: string[] | undefined;
}>;
export type StructuredSolutionResult = z.infer<typeof StructuredSolutionSchema>;
export declare function containsBrokenCharacters(text: string): boolean;
export declare function cleanBrokenCharacters(text: string): string;
