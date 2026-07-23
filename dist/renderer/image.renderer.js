"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.closeBrowserInstance = closeBrowserInstance;
exports.renderSolutionToPNG = renderSolutionToPNG;
const playwright_1 = __importDefault(require("playwright"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const latex_validator_1 = require("./latex.validator");
const logger_1 = require("../utils/logger");
let browserInstance = null;
async function getBrowser() {
    if (!browserInstance || !browserInstance.isConnected()) {
        logger_1.logger.info('Launching Playwright Chromium instance...');
        browserInstance = await playwright_1.default.chromium.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
        });
    }
    return browserInstance;
}
async function closeBrowserInstance() {
    if (browserInstance && browserInstance.isConnected()) {
        logger_1.logger.info('Closing Playwright Chromium instance...');
        await browserInstance.close();
        browserInstance = null;
    }
}
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
async function renderSolutionToPNG(result, outputPath, botName = 'Smart AI Assistant', botUsername = '@mysmart_v2_2026_bot') {
    const templatePath = path_1.default.join(__dirname, 'templates', 'solution.template.html');
    let templateHtml = fs_1.default.readFileSync(templatePath, 'utf8');
    // Build Questions HTML
    let questionsHtml = '';
    result.questions.forEach((q) => {
        const qLatex = (0, latex_validator_1.validateAndSanitizeLaTeX)(q.question_latex).renderedHtml;
        let stepsHtml = '';
        q.steps.forEach((step) => {
            const stepLatex = (0, latex_validator_1.validateAndSanitizeLaTeX)(step.latex).renderedHtml;
            stepsHtml += `
        <div class="step-item">
          <div class="step-explanation">${escapeHtml(step.explanation)}</div>
          <div class="math-display">${stepLatex}</div>
        </div>
      `;
        });
        const finalAnswerLatex = (0, latex_validator_1.validateAndSanitizeLaTeX)(q.final_answer_latex).renderedHtml;
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
    const browser = await getBrowser();
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 },
        deviceScaleFactor: 2, // High resolution PNG
    });
    const page = await context.newPage();
    try {
        try {
            await page.setContent(templateHtml, { waitUntil: 'domcontentloaded', timeout: 15000 });
        }
        catch (e) {
            logger_1.logger.warn('setContent domcontentloaded timeout, proceeding to screenshot');
        }
        // Wait for KaTeX and font rendering ready flag
        try {
            await page.waitForFunction(() => window.__RENDER_READY__ === true, { timeout: 10000 });
        }
        catch (e) {
            logger_1.logger.warn('KaTeX render ready flag timeout, proceeding to screenshot');
        }
        const cardElement = await page.$('#solution-card');
        if (cardElement) {
            await cardElement.screenshot({ path: outputPath, type: 'png' });
        }
        else {
            await page.screenshot({ path: outputPath, fullPage: true, type: 'png' });
        }
        logger_1.logger.info(`Successfully rendered solution PNG image to: ${outputPath}`);
        return outputPath;
    }
    finally {
        await context.close();
    }
}
//# sourceMappingURL=image.renderer.js.map