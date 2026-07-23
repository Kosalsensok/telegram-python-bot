import OpenAI from 'openai';
import { IAIProvider } from './base.provider';
import type { MathSolutionResult } from '../schemas/math-solution.schema';
import { MathSolutionResultSchema } from '../schemas/math-solution.schema';
import { getSystemPrompt } from '../prompts/system-prompt';
import { logger } from '../../utils/logger';
import { retryWithBackoff } from '../../utils/retry';

export class OpenAIProvider implements IAIProvider {
  public name = 'openai';
  private client: OpenAI;
  private model: string;

  constructor(apiKey: string, model: string = 'gpt-4o') {
    this.client = new OpenAI({ apiKey });
    this.model = model;
  }

  async analyzeAndSolveMathImage(
    imageBuffer: Buffer,
    mimeType: string,
    language: 'km' | 'en' = 'km',
    mode: string = 'standard'
  ): Promise<MathSolutionResult> {
    const base64Image = imageBuffer.toString('base64');
    const dataUrl = `data:${mimeType};base64,${base64Image}`;
    const prompt = getSystemPrompt(language, mode);

    return retryWithBackoff(async () => {
      logger.info(`Sending image request to OpenAI Vision API (${this.model})...`);
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
      return MathSolutionResultSchema.parse(parsed);
    }, 3, 1000);
  }
}
