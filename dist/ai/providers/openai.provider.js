"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpenAIProvider = void 0;
const openai_1 = __importDefault(require("openai"));
const math_solution_schema_1 = require("../schemas/math-solution.schema");
const system_prompt_1 = require("../prompts/system-prompt");
const logger_1 = require("../../utils/logger");
const retry_1 = require("../../utils/retry");
class OpenAIProvider {
    name = 'openai';
    client;
    model;
    constructor(apiKey, model = 'gpt-4o') {
        this.client = new openai_1.default({ apiKey });
        this.model = model;
    }
    async analyzeAndSolveMathImage(imageBuffer, mimeType, language = 'km', mode = 'standard') {
        const base64Image = imageBuffer.toString('base64');
        const dataUrl = `data:${mimeType};base64,${base64Image}`;
        const prompt = (0, system_prompt_1.getSystemPrompt)(language, mode);
        return (0, retry_1.retryWithBackoff)(async () => {
            logger_1.logger.info(`Sending image request to OpenAI Vision API (${this.model})...`);
            const response = await this.client.chat.completions.create({
                model: this.model,
                messages: [
                    { role: 'system', content: prompt },
                    {
                        role: 'user',
                        content: [
                            { type: 'text', text: 'Please extract and solve all math questions from this image.' },
                            { type: 'image_url', image_url: { url: dataUrl, detail: 'high' } }
                        ]
                    }
                ],
                response_format: { type: 'json_object' },
                max_tokens: 3000,
                temperature: 0.1,
            });
            const content = response.choices[0]?.message?.content;
            if (!content) {
                throw new Error('Empty response from OpenAI API');
            }
            const parsed = JSON.parse(content);
            return math_solution_schema_1.MathSolutionResultSchema.parse(parsed);
        }, 3, 1000);
    }
}
exports.OpenAIProvider = OpenAIProvider;
//# sourceMappingURL=openai.provider.js.map