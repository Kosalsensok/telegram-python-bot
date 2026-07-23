import { AIService } from '../ai/ai.service';
import { renderSolutionToPNG } from '../renderer/image.renderer';
import { renderSolutionToPDF } from '../renderer/pdf.renderer';
import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
import { getPrismaClient, isDatabaseConnected } from '../database/prisma';
import { generateRandomPublicId } from '../utils/sanitize';
import { logger } from '../utils/logger';
import path from 'path';
import { StorageService } from './storage.service';

export interface ProcessedSolutionOutput {
  publicId: string;
  imagePath: string;
  pdfPath: string;
  result: MathSolutionResult;
}

export class SolutionService {
  private aiService: AIService;
  private storageService: StorageService;

  constructor(aiService: AIService, storageService: StorageService) {
    this.aiService = aiService;
    this.storageService = storageService;
  }

  private inMemoryStore = new Map<string, any>();

  async processMathPhoto(
    telegramId: number,
    dbUserId: number,
    imageBuffer: Buffer,
    mimeType: string,
    language: 'km' | 'en' = 'km',
    mode: string = 'standard',
    telegramMessageId?: number
  ): Promise<ProcessedSolutionOutput> {
    const publicId = generateRandomPublicId();
    logger.info(`Starting math solution pipeline for user ${telegramId} [publicId: ${publicId}]...`);

    // 1. Solve image via AI provider abstraction
    const mathResult = await this.aiService.solveMathImage(imageBuffer, mimeType, language, mode);

    // 2. Render Solution PNG Image Card
    const imageFilename = `solution_${publicId}.png`;
    const imagePath = this.storageService.getTempPath(imageFilename);
    await renderSolutionToPNG(mathResult, imagePath);

    // 3. Render PDF Document
    const pdfFilename = `math-solution-${publicId}.pdf`;
    const pdfPath = this.storageService.getTempPath(pdfFilename);
    await renderSolutionToPDF(mathResult, pdfPath);

    // Store in local in-memory fallback store
    this.inMemoryStore.set(publicId, {
      publicId,
      subject: mathResult.subject || 'mathematics',
      extractedQuestion: mathResult.questions.map((q) => q.original_question).join('\n'),
      structuredResult: mathResult,
      status: 'COMPLETED',
      createdAt: new Date(),
    });

    // 4. Save Record to MySQL via Prisma
    const prisma = getPrismaClient();
    if (isDatabaseConnected() && prisma && dbUserId > 0) {
      try {
        await prisma.solution.create({
          data: {
            publicId,
            userId: dbUserId,
            telegramMessageId: telegramMessageId || null,
            outputImagePath: imagePath,
            outputPdfPath: pdfPath,
            subject: mathResult.subject || 'mathematics',
            extractedQuestion: mathResult.questions.map((q) => q.original_question).join('\n'),
            structuredResult: mathResult as any,
            status: 'COMPLETED',
          },
        });
      } catch (err) {
        logger.warn(`Failed storing solution record in DB for publicId ${publicId}:`, err);
      }
    }

    return {
      publicId,
      imagePath,
      pdfPath,
      result: mathResult,
    };
  }

  async getSolutionByPublicId(publicId: string) {
    if (publicId === 'demo123') {
      return {
        publicId: 'demo123',
        subject: 'mathematics',
        structuredResult: {
          language: 'km',
          subject: 'mathematics',
          title: 'ដំណោះស្រាយលំហាត់គណិតវិទ្យា (Demo Solution)',
          questions: [
            {
              number: 1,
              original_question: '(1 - 1/2)(1 - 1/3)(1 - 1/4)...(1 - 1/2024)',
              question_latex: '\\left(1-\\frac{1}{2}\\right)\\left(1-\\frac{1}{3}\\right)\\left(1-\\frac{1}{4}\\right)\\cdots\\left(1-\\frac{1}{2024}\\right)',
              steps: [
                {
                  explanation: 'បម្លែងកត្តានីមួយៗទៅជាប្រភាគ / Simplify each term into fractions',
                  latex: '= \\frac{1}{2} \\cdot \\frac{2}{3} \\cdot \\frac{3}{4} \\cdots \\frac{2023}{2024}',
                },
                {
                  explanation: 'សម្រួលភាគយក និងភាគបែងដែលដូចគ្នា / Simplify numerator and denominator terms',
                  latex: '= \\frac{1}{2024}',
                },
              ],
              final_answer_text: '1/2024',
              final_answer_latex: '\\boxed{\\frac{1}{2024}}',
            },
          ],
          notes: [],
        },
      };
    }

    if (this.inMemoryStore.has(publicId)) {
      return this.inMemoryStore.get(publicId);
    }

    const prisma = getPrismaClient();
    if (isDatabaseConnected() && prisma) {
      try {
        return await prisma.solution.findUnique({
          where: { publicId },
          include: { user: true },
        });
      } catch (err) {
        logger.warn(`Failed to fetch solution by publicId ${publicId} from DB:`, err);
      }
    }
    return null;
  }
}
