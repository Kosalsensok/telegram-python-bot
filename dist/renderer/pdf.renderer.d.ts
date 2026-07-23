import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
export declare function renderSolutionToPDF(result: MathSolutionResult, outputPath: string, botName?: string, botUsername?: string): Promise<string>;
