"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.StructuredSolutionSchema = exports.SectionSchema = exports.KeyValueSchema = exports.ResponseTypeEnum = void 0;
exports.containsBrokenCharacters = containsBrokenCharacters;
exports.cleanBrokenCharacters = cleanBrokenCharacters;
const zod_1 = require("zod");
exports.ResponseTypeEnum = zod_1.z.enum([
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
exports.KeyValueSchema = zod_1.z.object({
    label: zod_1.z.string(),
    value: zod_1.z.string(),
});
exports.SectionSchema = zod_1.z.object({
    id: zod_1.z.string().optional(),
    step_number: zod_1.z.number().optional(),
    type: zod_1.z.string().optional(),
    heading: zod_1.z.string().optional(),
    heading_km: zod_1.z.string().optional(),
    content: zod_1.z.string().optional(),
    content_km: zod_1.z.string().optional(),
    items: zod_1.z.array(zod_1.z.any()).optional(),
    tables: zod_1.z.array(zod_1.z.any()).optional(),
    endpoints: zod_1.z.array(zod_1.z.any()).optional(),
    language: zod_1.z.string().optional(),
    filename: zod_1.z.string().optional(),
    code: zod_1.z.string().optional(),
});
exports.StructuredSolutionSchema = zod_1.z.object({
    response_type: exports.ResponseTypeEnum,
    language: zod_1.z.string().default('km'),
    title: zod_1.z.string(),
    subtitle: zod_1.z.string().optional(),
    summary: zod_1.z.string().optional(),
    summary_km: zod_1.z.string().optional(),
    tags: zod_1.z.array(zod_1.z.string()).default([]),
    sections: zod_1.z.array(exports.SectionSchema).default([]),
    key_values: zod_1.z.array(exports.KeyValueSchema).default([]),
    warnings: zod_1.z.array(zod_1.z.string()).default([]),
    recommendations: zod_1.z.array(zod_1.z.string()).default([]),
    math_expressions: zod_1.z.array(zod_1.z.string()).default([]),
    suggested_actions: zod_1.z.array(zod_1.z.string()).default([]),
});
function containsBrokenCharacters(text) {
    if (!text)
        return false;
    const brokenPatterns = ['\u25A1', '\uFFFD', '\u25A0', '\u25A2', '\u25A3'];
    return brokenPatterns.some((pattern) => text.includes(pattern));
}
function cleanBrokenCharacters(text) {
    if (!text)
        return '';
    let cleaned = text.normalize('NFC');
    cleaned = cleaned.replace(/[\u25A1\u25A0\u25A2\u25A3\u25A4\u25A5]/g, '•');
    cleaned = cleaned.replace(/\uFFFD/g, '');
    cleaned = cleaned.replace(/•\s*•+/g, '•');
    return cleaned.trim();
}
//# sourceMappingURL=response-type.schema.js.map