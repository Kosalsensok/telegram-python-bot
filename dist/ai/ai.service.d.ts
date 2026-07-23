import { MathSolutionResult } from './schemas/math-solution.schema';
export declare class AIService {
    private primaryProvider;
    private fallbackProvider?;
    constructor();
    solveMathImage(imageBuffer: Buffer, mimeType: string, language?: 'km' | 'en', mode?: string): Promise<MathSolutionResult>;
}
