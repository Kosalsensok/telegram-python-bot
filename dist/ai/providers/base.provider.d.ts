import { MathSolutionResult } from '../schemas/math-solution.schema';
export interface IAIProvider {
    name: string;
    analyzeAndSolveMathImage(imageBuffer: Buffer, mimeType: string, language?: 'km' | 'en', mode?: string): Promise<MathSolutionResult>;
}
