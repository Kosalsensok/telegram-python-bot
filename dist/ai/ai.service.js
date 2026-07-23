"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AIService = void 0;
const gemini_provider_1 = require("./providers/gemini.provider");
const openai_provider_1 = require("./providers/openai.provider");
const env_1 = require("../config/env");
const logger_1 = require("../utils/logger");
class AIService {
    primaryProvider;
    fallbackProvider;
    constructor() {
        if (env_1.env.AI_PROVIDER === 'openai' && env_1.env.OPENAI_API_KEY) {
            this.primaryProvider = new openai_provider_1.OpenAIProvider(env_1.env.OPENAI_API_KEY, env_1.env.OPENAI_MODEL);
            if (env_1.env.GEMINI_API_KEY) {
                this.fallbackProvider = new gemini_provider_1.GeminiProvider(env_1.env.GEMINI_API_KEY, env_1.env.GEMINI_MODEL);
            }
        }
        else if (env_1.env.GEMINI_API_KEY) {
            this.primaryProvider = new gemini_provider_1.GeminiProvider(env_1.env.GEMINI_API_KEY, env_1.env.GEMINI_MODEL);
            if (env_1.env.OPENAI_API_KEY) {
                this.fallbackProvider = new openai_provider_1.OpenAIProvider(env_1.env.OPENAI_API_KEY, env_1.env.OPENAI_MODEL);
            }
        }
        else {
            throw new Error('No valid AI provider API keys configured in environment.');
        }
    }
    async solveMathImage(imageBuffer, mimeType, language = 'km', mode = 'standard') {
        try {
            logger_1.logger.info(`Solving math image using primary provider: ${this.primaryProvider.name}`);
            return await this.primaryProvider.analyzeAndSolveMathImage(imageBuffer, mimeType, language, mode);
        }
        catch (primaryError) {
            logger_1.logger.warn(`Primary provider ${this.primaryProvider.name} failed:`, primaryError);
            if (this.fallbackProvider) {
                logger_1.logger.info(`Attempting fallback provider: ${this.fallbackProvider.name}`);
                return await this.fallbackProvider.analyzeAndSolveMathImage(imageBuffer, mimeType, language, mode);
            }
            throw primaryError;
        }
    }
}
exports.AIService = AIService;
//# sourceMappingURL=ai.service.js.map