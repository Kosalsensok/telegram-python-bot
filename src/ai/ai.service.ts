import { IAIProvider } from './providers/base.provider';
import { GeminiProvider } from './providers/gemini.provider';
import { OpenAIProvider } from './providers/openai.provider';
import { MathSolutionResult } from './schemas/math-solution.schema';
import { env } from '../config/env';
import { logger } from '../utils/logger';

export class AIService {
  private primaryProvider: IAIProvider;
  private fallbackProvider?: IAIProvider;

  constructor() {
    if (env.AI_PROVIDER === 'openai' && env.OPENAI_API_KEY) {
      this.primaryProvider = new OpenAIProvider(env.OPENAI_API_KEY, env.OPENAI_MODEL);
      if (env.GEMINI_API_KEY) {
        this.fallbackProvider = new GeminiProvider(env.GEMINI_API_KEY, env.GEMINI_MODEL);
      }
    } else if (env.GEMINI_API_KEY) {
      this.primaryProvider = new GeminiProvider(env.GEMINI_API_KEY, env.GEMINI_MODEL);
      if (env.OPENAI_API_KEY) {
        this.fallbackProvider = new OpenAIProvider(env.OPENAI_API_KEY, env.OPENAI_MODEL);
      }
    } else {
      throw new Error('No valid AI provider API keys configured in environment.');
    }
  }

  async solveMathImage(
    imageBuffer: Buffer,
    mimeType: string,
    language: 'km' | 'en' = 'km',
    mode: string = 'standard'
  ): Promise<MathSolutionResult> {
    try {
      logger.info(`Solving math image using primary provider: ${this.primaryProvider.name}`);
      return await this.primaryProvider.analyzeAndSolveMathImage(imageBuffer, mimeType, language, mode);
    } catch (primaryError) {
      logger.warn(`Primary provider ${this.primaryProvider.name} failed:`, primaryError);
      if (this.fallbackProvider) {
        logger.info(`Attempting fallback provider: ${this.fallbackProvider.name}`);
        return await this.fallbackProvider.analyzeAndSolveMathImage(imageBuffer, mimeType, language, mode);
      }
      throw primaryError;
    }
  }
}
