import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
export declare function closeBrowserInstance(): Promise<void>;
export declare function renderSolutionToPNG(result: MathSolutionResult, outputPath: string, botName?: string, botUsername?: string): Promise<string>;
