import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
import { StructuredSolutionResult } from '../ai/schemas/response-type.schema';
export declare function renderSolutionToPDF(result: MathSolutionResult | StructuredSolutionResult | any, outputPath: string, botName?: string, botUsername?: string): Promise<string>;
