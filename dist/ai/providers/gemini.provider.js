"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GeminiProvider = void 0;
const generative_ai_1 = require("@google/generative-ai");
const math_solution_schema_1 = require("../schemas/math-solution.schema");
const system_prompt_1 = require("../prompts/system-prompt");
const logger_1 = require("../../utils/logger");
const retry_1 = require("../../utils/retry");
class GeminiProvider {
    name = 'gemini';
    genAI;
    modelName;
    constructor(apiKey, modelName = 'gemini-2.0-flash') {
        this.genAI = new generative_ai_1.GoogleGenerativeAI(apiKey);
        this.modelName = modelName;
    }
    async analyzeAndSolveMathImage(imageBuffer, mimeType, language = 'km', mode = 'standard') {
        const prompt = (0, system_prompt_1.getSystemPrompt)(language, mode);
        return (0, retry_1.retryWithBackoff)(async () => {
            logger_1.logger.info(`Sending image request to Gemini Vision API (${this.modelName})...`);
            const model = this.genAI.getGenerativeModel({
                model: this.modelName,
                generationConfig: {
                    responseMimeType: 'application/json',
                    temperature: 0.1,
                },
            });
            const imagePart = {
                inlineData: {
                    data: imageBuffer.toString('base64'),
                    mimeType: mimeType || 'image/jpeg',
                },
            };
            const result = await model.generateContent([prompt, imagePart]);
            const responseText = result.response.text();
            if (!responseText) {
                throw new Error('Empty response from Gemini API');
            }
            const cleaned = responseText.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
            const parsed = JSON.parse(cleaned);
            return math_solution_schema_1.MathSolutionResultSchema.parse(parsed);
        }, 3, 1000);
    }
}
exports.GeminiProvider = GeminiProvider;
//# sourceMappingURL=gemini.provider.js.map