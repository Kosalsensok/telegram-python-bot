import playwright from 'playwright';
import fs from 'fs';
import path from 'path';
import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
import { validateAndSanitizeLaTeX } from './latex.validator';
import { logger } from '../utils/logger';

export async function renderSolutionToPDF(
  result: MathSolutionResult,
  outputPath: string,
  botName: string = 'Smart AI Assistant',
  botUsername: string = '@mysmart_v2_2026_bot'
): Promise<string> {
  const templatePath = path.join(__dirname, 'templates', 'solution.template.html');
  let templateHtml = fs.readFileSync(templatePath, 'utf8');

  // Build Questions HTML
  let questionsHtml = '';
  result.questions.forEach((q) => {
    const qLatex = validateAndSanitizeLaTeX(q.question_latex).renderedHtml;
    
    let stepsHtml = '';
    q.steps.forEach((step) => {
      const stepLatex = validateAndSanitizeLaTeX(step.latex).renderedHtml;
      stepsHtml += `
        <div class="step-item">
          <div class="step-explanation">${escapeHtml(step.explanation)}</div>
          <div class="math-display">${stepLatex}</div>
        </div>
      `;
    });

    const finalAnswerLatex = validateAndSanitizeLaTeX(q.final_answer_latex).renderedHtml;

    questionsHtml += `
      <div class="question-block">
        <div class="question-title">
          <span>សំណួរទី ${q.number} (Problem ${q.number})</span>
        </div>
        <div class="math-display">${qLatex}</div>
        <div class="steps-container">
          ${stepsHtml}
        </div>
        <div class="final-answer-box">
          <div class="label">ចម្លើយចុងក្រោយ / Final Answer</div>
          <div class="math-display">${finalAnswerLatex}</div>
        </div>
      </div>
    `;
  });

  const nowStr = new Date().toLocaleString('en-US', { timeZone: 'Asia/Phnom_Penh' });

  templateHtml = templateHtml
    .replace('{{TITLE}}', escapeHtml(result.title || 'Math Solution'))
    .replace('{{BOT_NAME}}', escapeHtml(botName))
    .replace('{{BOT_USERNAME}}', escapeHtml(botUsername))
    .replace('{{SUBJECT}}', escapeHtml((result.subject || 'MATHEMATICS').toUpperCase()))
    .replace('{{QUESTIONS_CONTENT}}', questionsHtml)
    .replace('{{GENERATED_AT}}', nowStr);

  const browser = await playwright.chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  try {
    await page.setContent(templateHtml, { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => (window as any).__RENDER_READY__ === true, { timeout: 10000 });

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

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
