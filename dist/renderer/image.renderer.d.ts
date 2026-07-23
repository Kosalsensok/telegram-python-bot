import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
export declare function renderSolutionToPNG(result: MathSolutionResult, outputPath: string, botName?: string, botUsername?: string): Promise<string>;
export declare function closeBrowserInstance(): Promise<void>;
