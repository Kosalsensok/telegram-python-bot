import { AIService } from '../ai/ai.service';
import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
import { StorageService } from './storage.service';
export interface ProcessedSolutionOutput {
    publicId: string;
    imagePath: string;
    pdfPath: string;
    result: MathSolutionResult;
}
export declare class SolutionService {
    private aiService;
    private storageService;
    constructor(aiService: AIService, storageService: StorageService);
    private inMemoryStore;
    processMathPhoto(telegramId: number, dbUserId: number, imageBuffer: Buffer, mimeType: string, language?: 'km' | 'en', mode?: string, telegramMessageId?: number): Promise<ProcessedSolutionOutput>;
    getSolutionByPublicId(publicId: string): Promise<any>;
}
