import playwright, { Browser } from 'playwright';
import fs from 'fs';
import path from 'path';
import { MathSolutionResult } from '../ai/schemas/math-solution.schema';
import { StructuredSolutionResult, cleanBrokenCharacters } from '../ai/schemas/response-type.schema';
import { validateAndSanitizeLaTeX } from './latex.validator';
import { logger } from '../utils/logger';

let browserInstance: Browser | null = null;

async function getBrowser(): Promise<Browser> {
  if (!browserInstance || !browserInstance.isConnected()) {
    logger.info('Launching Playwright Chromium instance...');
    browserInstance = await playwright.chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
  }
  return browserInstance;
}

export async function closeBrowserInstance(): Promise<void> {
  if (browserInstance && browserInstance.isConnected()) {
    logger.info('Closing Playwright Chromium instance...');
    await browserInstance.close();
    browserInstance = null;
  }
}

function escapeHtml(unsafe: string): string {
  if (!unsafe) return '';
  return cleanBrokenCharacters(unsafe)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function buildSolutionHtml(
  data: StructuredSolutionResult | any,
  botName: string = 'Smart AI Assistant',
  botUsername: string = '@mysmart_v2_2026_bot'
): string {
  const templatePath = path.join(__dirname, 'templates', 'solution.template.html');
  let templateHtml = fs.readFileSync(templatePath, 'utf8');

  const resType = data.response_type || 'general_image';
  const typeLabels: Record<string, string> = {
    email: '📧 ការវិភាគអ៊ីមែល',
    document: '📄 ការវិភាគឯកសារ',
    table: '📊 ការវិភាគតារាង',
    mathematics: '🎓 គណិតវិទ្យា',
    chemistry: '🧪 គីមីវិទ្យា',
    physics: '⚡ រូបវិទ្យា',
    general_image: '🖼 ការវិភាគរូបភាព',
  };

  let mainContentHtml = '';

  // 1. Summary Section
  if (data.summary) {
    mainContentHtml += `
      <section class="summary-card">
        <h2>សេចក្តីសង្ខេប (Summary)</h2>
        <p>${escapeHtml(data.summary)}</p>
      </section>
    `;
  }

  // 2. Key Values Grid
  if (data.key_values && data.key_values.length > 0) {
    let rowsHtml = '';
    data.key_values.forEach((kv: any) => {
      rowsHtml += `
        <div class="data-row">
          <div class="data-label">${escapeHtml(kv.label)}</div>
          <div class="data-value">${escapeHtml(kv.value)}</div>
        </div>
      `;
    });
    mainContentHtml += `
      <section class="data-grid">
        <h2>ព័ត៌មានសំខាន់ (Key Information)</h2>
        ${rowsHtml}
      </section>
    `;
  }

  // 3. Structured Sections / Math Questions
  if (data.questions && Array.isArray(data.questions)) {
    data.questions.forEach((q: any) => {
      const qLatex = validateAndSanitizeLaTeX(q.question_latex || '').renderedHtml;
      let stepsHtml = '';
      if (q.steps && Array.isArray(q.steps)) {
        q.steps.forEach((s: any) => {
          const stepLatex = validateAndSanitizeLaTeX(s.latex || '').renderedHtml;
          stepsHtml += `
            <div class="step-item">
              <div class="step-explanation">${escapeHtml(s.explanation || '')}</div>
              <div class="math-display">${stepLatex}</div>
            </div>
          `;
        });
      }
      const finalLatex = validateAndSanitizeLaTeX(q.final_answer_latex || '').renderedHtml;
      mainContentHtml += `
        <div class="question-block">
          <div class="question-title">សំណួរទី ${q.number || 1}</div>
          <div class="math-display">${qLatex}</div>
          <div class="steps-container">${stepsHtml}</div>
          <div class="final-answer-box">
            <div class="label">ចម្លើយចុងក្រោយ / Final Answer</div>
            <div class="math-display">${finalLatex}</div>
          </div>
        </div>
      `;
    });
  } else if (data.sections && Array.isArray(data.sections)) {
    data.sections.forEach((sec: any) => {
      mainContentHtml += `
        <section class="section-card">
          <h2>${escapeHtml(sec.heading || 'ព័ត៌មាន')}</h2>
          <div class="content-text">${escapeHtml(sec.content || '').replace(/\n/g, '<br/>')}</div>
        </section>
      `;
    });
  }

  // 4. Warnings
  if (data.warnings && data.warnings.length > 0) {
    let warnHtml = '';
    data.warnings.forEach((w: string) => {
      warnHtml += `<div class="bullet-item"><span class="bullet-text">${escapeHtml(w)}</span></div>`;
    });
    mainContentHtml += `
      <section class="warning-card">
        <h2>⚠️ ការប្រុងប្រយ័ត្ន (Warnings)</h2>
        ${warnHtml}
      </section>
    `;
  }

  // 5. Recommendations
  if (data.recommendations && data.recommendations.length > 0) {
    let recHtml = '';
    data.recommendations.forEach((r: string) => {
      recHtml += `<div class="bullet-item"><span class="bullet-text">${escapeHtml(r)}</span></div>`;
    });
    mainContentHtml += `
      <section class="recommendation-card">
        <h2>💡 អនុសាសន៍ (Recommendations)</h2>
        ${recHtml}
      </section>
    `;
  }

  const nowStr = new Date().toLocaleString('en-US', { timeZone: 'Asia/Phnom_Penh' });

  templateHtml = templateHtml
    .replace('{{TITLE}}', escapeHtml(data.title || 'Solution Card'))
    .replace(/\{\{BOT_NAME\}\}/g, escapeHtml(botName))
    .replace(/\{\{BOT_USERNAME\}\}/g, escapeHtml(botUsername))
    .replace('{{RESPONSE_TYPE_LABEL}}', typeLabels[resType] || '🖼 ការវិភាគ')
    .replace('{{MAIN_CONTENT}}', mainContentHtml)
    .replace('{{GENERATED_AT}}', nowStr);

  return templateHtml;
}

export async function renderSolutionToPNG(
  result: MathSolutionResult | StructuredSolutionResult | any,
  outputPath: string,
  botName: string = 'Smart AI Assistant',
  botUsername: string = '@mysmart_v2_2026_bot'
): Promise<string> {
  const htmlContent = buildSolutionHtml(result, botName, botUsername);

  const browser = await getBrowser();
  const context = await browser.newContext({
    viewport: { width: 1100, height: 900 },
    deviceScaleFactor: 2, // High DPI screenshot
  });

  const page = await context.newPage();
  try {
    await page.setContent(htmlContent, { waitUntil: 'load', timeout: 15000 });

    // Ensure fonts and KaTeX rendering are ready
    await page.evaluate(async () => {
      if (document.fonts) {
        await document.fonts.ready;
      }
    });

    try {
      await page.waitForFunction(() => (window as any).__RENDER_READY__ === true, { timeout: 8000 });
    } catch (e) {
      logger.warn('Render ready timeout, proceeding to screenshot');
    }

    const cardElement = await page.$('#solution-card');
    if (cardElement) {
      await cardElement.screenshot({ path: outputPath, type: 'png' });
    } else {
      await page.screenshot({ path: outputPath, fullPage: true, type: 'png' });
    }

    logger.info(`Successfully rendered PNG image to: ${outputPath}`);
    return outputPath;
  } finally {
    await context.close();
  }
}
