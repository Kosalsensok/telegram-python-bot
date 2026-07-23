"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SolutionService = void 0;
const image_renderer_1 = require("../renderer/image.renderer");
const pdf_renderer_1 = require("../renderer/pdf.renderer");
const prisma_1 = require("../database/prisma");
const sanitize_1 = require("../utils/sanitize");
const logger_1 = require("../utils/logger");
class SolutionService {
    aiService;
    storageService;
    constructor(aiService, storageService) {
        this.aiService = aiService;
        this.storageService = storageService;
    }
    inMemoryStore = new Map();
    async processMathPhoto(telegramId, dbUserId, imageBuffer, mimeType, language = 'km', mode = 'standard', telegramMessageId) {
        const publicId = (0, sanitize_1.generateRandomPublicId)();
        logger_1.logger.info(`Starting math solution pipeline for user ${telegramId} [publicId: ${publicId}]...`);
        // 1. Solve image via AI provider abstraction
        const mathResult = await this.aiService.solveMathImage(imageBuffer, mimeType, language, mode);
        // 2. Render Solution PNG Image Card
        const imageFilename = `solution_${publicId}.png`;
        const imagePath = this.storageService.getTempPath(imageFilename);
        await (0, image_renderer_1.renderSolutionToPNG)(mathResult, imagePath);
        // 3. Render PDF Document
        const pdfFilename = `math-solution-${publicId}.pdf`;
        const pdfPath = this.storageService.getTempPath(pdfFilename);
        await (0, pdf_renderer_1.renderSolutionToPDF)(mathResult, pdfPath);
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
        const prisma = (0, prisma_1.getPrismaClient)();
        if ((0, prisma_1.isDatabaseConnected)() && prisma && dbUserId > 0) {
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
                        structuredResult: mathResult,
                        status: 'COMPLETED',
                    },
                });
            }
            catch (err) {
                logger_1.logger.warn(`Failed storing solution record in DB for publicId ${publicId}:`, err);
            }
        }
        return {
            publicId,
            imagePath,
            pdfPath,
            result: mathResult,
        };
    }
    async getSolutionByPublicId(publicId) {
        if (publicId === 'demo123') {
            return {
                publicId: 'demo123',
                subject: 'Mathematics',
                topic: 'Fraction Multiplication',
                difficulty: 'Easy',
                language: 'km-en',
                verified: true,
                generatedAt: 'July 23, 2026',
                generatedTime: '10:22 AM',
                modelName: 'Smart AI Math Solver (Gemini 2.0 Flash)',
                summary: 'សម្រួលកត្តានីមួយៗនៃផលគុណប្រភាគ រួចធ្វើការសម្រួលភាគយក និងភាគបែងដែលដូចគ្នាតាមលំនាំតទល់ (Telescoping Product)។ / Simplify each term into fractions and cancel adjacent numerators and denominators using telescoping multiplication.',
                structuredResult: {
                    language: 'km',
                    subject: 'Mathematics',
                    topic: 'Fraction Multiplication',
                    difficulty: 'Easy',
                    title: 'ដំណោះស្រាយលំហាត់គណិតវិទ្យា (Official Solution)',
                    questions: [
                        {
                            number: 1,
                            original_question: '(1 - 1/2)(1 - 1/3)(1 - 1/4)...(1 - 1/2024)',
                            question_latex: '\\left(1 - \\frac{1}{2}\\right)\\left(1 - \\frac{1}{3}\\right)\\left(1 - \\frac{1}{4}\\right)\\cdots\\left(1 - \\frac{1}{2024}\\right)',
                            steps: [
                                {
                                    id: 'step-1',
                                    title: 'Simplify Each Term',
                                    titleKh: 'បម្លែងកត្តានីមួយៗទៅជាប្រភាគទោល',
                                    explanation: 'កត្តាទូទៅក្នុងទម្រង់ 1 - 1/n អាចសរសេរជាប្រភាគ (n - 1)/n សម្រាប់ n = 2, 3, 4, ..., 2024។ / Apply the algebraic identity 1 - 1/n = (n - 1)/n to every factor in the product.',
                                    latex: '= \\left(\\frac{1}{2}\\right) \\cdot \\left(\\frac{2}{3}\\right) \\cdot \\left(\\frac{3}{4}\\right) \\cdots \\left(\\frac{2023}{2024}\\right)',
                                    note: 'ចំណាំ៖ ភាគយកនៃកត្តានីមួយៗមានតម្លៃតិចជាងភាគបែងរបស់វាចំនួន ១។ / Note: Each numerator is exactly 1 less than its denominator.',
                                },
                                {
                                    id: 'step-2',
                                    title: 'Identify the Cancellation Pattern',
                                    titleKh: 'កំណត់លំនាំនៃការសម្រួលភាគយក និងភាគបែង',
                                    explanation: 'សង្កេតឃើញថាភាគបែងនៃប្រភាគនីមួយៗនឹងត្រូវសម្រួលចោលជាមួយភាគយកនៃប្រភាគបន្ទាប់ (Telescoping Cancellation)។ / Observe that the denominator of each term cancels out with the numerator of the subsequent term.',
                                    latex: '= \\frac{1}{\\bcancel{2}} \\cdot \\frac{\\bcancel{2}}{\\bcancel{3}} \\cdot \\frac{\\bcancel{3}}{\\bcancel{4}} \\cdots \\frac{\\bcancel{2023}}{2024}',
                                    note: 'កត្តាកណ្តាលទាំងអស់ត្រូវបានសម្រួលអស់។ / All intermediate numerators and denominators cancel out completely.',
                                },
                                {
                                    id: 'step-3',
                                    title: 'Simplify the Product',
                                    titleKh: 'សម្រួលផលគុណចុងក្រោយ',
                                    explanation: 'បន្ទាប់ពីសម្រួលរួច នៅសល់តែភាគយកទី១ (ស្មើនឹង ១) និងភាគបែងចុងក្រោយ (ស្មើនឹង ២០២៤) ប៉ុណ្ណោះ។ / After cancelling all middle terms, only the first numerator (1) and the final denominator (2024) remain.',
                                    latex: '= \\frac{1 \\times 1 \\times \\dots \\times 1}{1 \\times 1 \\times \\dots \\times 2024} = \\frac{1}{2024}',
                                },
                                {
                                    id: 'step-4',
                                    title: 'Final Result',
                                    titleKh: 'ចម្លើយចុងក្រោយពេញលេញ',
                                    explanation: 'តម្លៃនៃផលគុណប្រភាគសរុបគឺស្មើនឹង ១/២០២៤។ / The simplified value of the infinite-like telescoping sequence is 1/2024.',
                                    latex: '\\boxed{\\frac{1}{2024}}',
                                },
                            ],
                            final_answer_text: '1/2024',
                            final_answer_latex: '\\frac{1}{2024}',
                        },
                    ],
                    notes: [
                        'ត្រូវប្រយ័ត្ន៖ កុំគុណលេខធំៗបញ្ចូលគ្នាមុនពេលសម្រួល (Always cancel before multiplying large numbers).',
                        'វិធីសាស្រ្តនេះហៅថា Telescoping Product ( Telescoping sequence cancellation technique ).',
                    ],
                },
            };
        }
        if (this.inMemoryStore.has(publicId)) {
            return this.inMemoryStore.get(publicId);
        }
        const prisma = (0, prisma_1.getPrismaClient)();
        if ((0, prisma_1.isDatabaseConnected)() && prisma) {
            try {
                return await prisma.solution.findUnique({
                    where: { publicId },
                    include: { user: true },
                });
            }
            catch (err) {
                logger_1.logger.warn(`Failed to fetch solution by publicId ${publicId} from DB:`, err);
            }
        }
        return null;
    }
}
exports.SolutionService = SolutionService;
//# sourceMappingURL=solution.service.js.map