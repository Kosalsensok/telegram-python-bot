import playwright from 'playwright';
import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
import { StructuredSolutionResult } from '../ai/schemas/response-type.schema';
import { buildSolutionHtml } from './image.renderer';
import { logger } from '../utils/logger';

export async function renderSolutionToPDF(
  result: MathSolutionResult | StructuredSolutionResult | any,
  outputPath: string,
  botName: string = 'Smart AI Assistant',
  botUsername: string = '@mysmart_v2_2026_bot'
): Promise<string> {
  const htmlContent = buildSolutionHtml(result, botName, botUsername);

  const browser = await playwright.chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  try {
    await page.setContent(htmlContent, { waitUntil: 'load', timeout: 15000 });

    await page.evaluate(async () => {
      if (document.fonts) {
        await document.fonts.ready;
      }
    });

    try {
      await page.waitForFunction(() => (window as any).__RENDER_READY__ === true, { timeout: 8000 });
    } catch (e) {
      logger.warn('Render ready timeout for PDF, proceeding');
    }

    await page.pdf({
      path: outputPath,
      format: 'A4',
      margin: { top: '15mm', bottom: '15mm', left: '15mm', right: '15mm' },
      printBackground: true,
    });

    logger.info(`Successfully generated solution PDF document to: ${outputPath}`);
    return outputPath;
  } finally {
    await page.close();
    await browser.close();
  }
}
