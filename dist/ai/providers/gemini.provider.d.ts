import { IAIProvider } from './base.provider';
import type { MathSolutionResult } from '../schemas/math-solution.schema';
export declare class GeminiProvider implements IAIProvider {
    name: string;
    private genAI;
    private modelName;
    constructor(apiKey: string, modelName?: string);
    analyzeAndSolveMathImage(imageBuffer: Buffer, mimeType: string, language?: 'km' | 'en', mode?: string): Promise<MathSolutionResult>;
}
