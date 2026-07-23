import { GoogleGenerativeAI } from '@google/generative-ai';
import { IAIProvider } from './base.provider';
import type { MathSolutionResult } from '../schemas/math-solution.schema';
import { MathSolutionResultSchema } from '../schemas/math-solution.schema';
import { getSystemPrompt } from '../prompts/system-prompt';
import { logger } from '../../utils/logger';
import { retryWithBackoff } from '../../utils/retry';

export class GeminiProvider implements IAIProvider {
  public name = 'gemini';
  private genAI: GoogleGenerativeAI;
  private modelName: string;

  constructor(apiKey: string, modelName: string = 'gemini-2.0-flash') {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.modelName = modelName;
  }

  async analyzeAndSolveMathImage(
    imageBuffer: Buffer,
    mimeType: string,
    language: 'km' | 'en' = 'km',
    mode: string = 'standard'
  ): Promise<MathSolutionResult> {
    const prompt = getSystemPrompt(language, mode);

    return retryWithBackoff(async () => {
      logger.info(`Sending image request to Gemini Vision API (${this.modelName})...`);
      
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
      return MathSolutionResultSchema.parse(parsed);
    }, 3, 1000);
  }
}
