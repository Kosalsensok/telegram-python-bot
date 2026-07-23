import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
import { StructuredSolutionResult } from '../ai/schemas/response-type.schema';
export declare function closeBrowserInstance(): Promise<void>;
export declare function buildSolutionHtml(data: StructuredSolutionResult | any, botName?: string, botUsername?: string): string;
export declare function renderSolutionToPNG(result: MathSolutionResult | StructuredSolutionResult | any, outputPath: string, botName?: string, botUsername?: string): Promise<string>;
