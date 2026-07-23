"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.StructuredSolutionSchema = exports.SectionSchema = exports.KeyValueSchema = void 0;
exports.containsBrokenCharacters = containsBrokenCharacters;
exports.cleanBrokenCharacters = cleanBrokenCharacters;
const zod_1 = require("zod");
exports.KeyValueSchema = zod_1.z.object({
    label: zod_1.z.string(),
    value: zod_1.z.string(),
});
exports.SectionSchema = zod_1.z.object({
    heading: zod_1.z.string(),
    content: zod_1.z.string(),
});
exports.StructuredSolutionSchema = zod_1.z.object({
    response_type: zod_1.z.enum([
        'mathematics',
        'chemistry',
        'physics',
        'email',
        'document',
        'table',
        'general_image',
    ]),
    language: zod_1.z.string().default('km'),
    title: zod_1.z.string(),
    summary: zod_1.z.string(),
    sections: zod_1.z.array(exports.SectionSchema).default([]),
    key_values: zod_1.z.array(exports.KeyValueSchema).default([]),
    warnings: zod_1.z.array(zod_1.z.string()).default([]),
    recommendations: zod_1.z.array(zod_1.z.string()).default([]),
    math_expressions: zod_1.z.array(zod_1.z.string()).default([]),
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