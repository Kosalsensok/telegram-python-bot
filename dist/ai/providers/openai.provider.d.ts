import { IAIProvider } from './base.provider';
import type { MathSolutionResult } from '../schemas/math-solution.schema';
export declare class OpenAIProvider implements IAIProvider {
    name: string;
    private client;
    private model;
    constructor(apiKey: string, model?: string);
    analyzeAndSolveMathImage(imageBuffer: Buffer, mimeType: string, language?: 'km' | 'en', mode?: string): Promise<MathSolutionResult>;
}
