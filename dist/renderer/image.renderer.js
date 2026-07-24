"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.closeBrowserInstance = closeBrowserInstance;
exports.buildSolutionHtml = buildSolutionHtml;
exports.renderSolutionToPNG = renderSolutionToPNG;
const playwright_1 = __importDefault(require("playwright"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const response_type_schema_1 = require("../ai/schemas/response-type.schema");
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
    if (!unsafe)
        return '';
    return (0, response_type_schema_1.cleanBrokenCharacters)(unsafe)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
function buildSolutionHtml(data, botName = 'Smart AI Assistant', botUsername = '@mysmart_v2_2026_bot') {
    const templatePath = path_1.default.join(__dirname, 'templates', 'solution.template.html');
    let templateHtml = fs_1.default.readFileSync(templatePath, 'utf8');
    const resType = data.response_type || 'general_answer';
    const typeLabels = {
        general_answer: '🤖 General AI Answer',
        code_answer: '💻 Code Solution',
        technical_explanation: '🧠 Technical Explanation',
        software_requirements: '🛒 System Requirements',
        project_prototype: '📦 Project Prototype',
        system_architecture: '🏛 Architecture Design',
        database_design: '🗄 Database Schema',
        api_design: '🔌 API Specification',
        mathematics: '🎓 Math Solution',
        chemistry: '🧪 Chemistry Analysis',
        physics: '⚡ Physics Solution',
        email_analysis: '📧 Email Analysis',
        email: '📧 Email Analysis',
        document_analysis: '📄 Document Analysis',
        document: '📄 Document Analysis',
        table_analysis: '📊 Table Extraction',
        table: '📊 Table Extraction',
        general_image_analysis: '🖼 Image Analysis',
        general_image: '🖼 Image Analysis',
    };
    // Build Tags HTML
    let tagsHtml = '';
    if (data.tags && Array.isArray(data.tags)) {
        data.tags.forEach((tag) => {
            tagsHtml += `<span>${escapeHtml(tag)}</span>`;
        });
    }
    // Build Stepper Rows (Form A CSS Stepper)
    let stepperRowsHtml = '';
    let stepNumber = 1;
    // Key Values Grid as Step 1 if available
    if (data.key_values && data.key_values.length > 0) {
        let rowsHtml = '';
        data.key_values.forEach((kv) => {
            rowsHtml += `
        <div class="data-row">
          <div class="data-label">${escapeHtml(kv.label)}</div>
          <div class="data-value">${escapeHtml(kv.value)}</div>
        </div>
      `;
        });
        stepperRowsHtml += `
      <div class="step-row">
        <div class="step-rail">
          <div class="step-marker">${stepNumber++}</div>
          <div class="step-line"></div>
        </div>
        <section class="step-content">
          <div class="step-card">
            <h2>📌 ព័ត៌មានសំខាន់ (Key Information)</h2>
            <div class="data-grid">${rowsHtml}</div>
          </div>
        </section>
      </div>
    `;
    }
    // Structured Sections as Stepper Steps
    if (data.sections && Array.isArray(data.sections)) {
        data.sections.forEach((sec) => {
            const heading = escapeHtml(sec.heading_km || sec.heading || `ផ្នែកទី ${stepNumber}`);
            let bodyHtml = '';
            if (sec.content_km || sec.content) {
                const textContent = sec.content_km || sec.content;
                bodyHtml += `<div class="step-text">${escapeHtml(textContent).replace(/\n/g, '<br/>')}</div>`;
            }
            if (sec.code) {
                bodyHtml += `<pre class="code-block"><code>${escapeHtml(sec.code)}</code></pre>`;
            }
            if (sec.items && Array.isArray(sec.items)) {
                sec.items.forEach((item) => {
                    if (typeof item === 'string') {
                        bodyHtml += `<div class="step-text">• ${escapeHtml(item)}</div>`;
                    }
                    else if (typeof item === 'object' && item !== null) {
                        const itemTitle = item.title ? `<b>${escapeHtml(item.title)}</b>: ` : '';
                        const itemDesc = item.description_km || item.description || JSON.stringify(item);
                        bodyHtml += `<div class="step-text">• ${itemTitle}${escapeHtml(itemDesc)}</div>`;
                    }
                });
            }
            stepperRowsHtml += `
        <div class="step-row">
          <div class="step-rail">
            <div class="step-marker">${sec.step_number || stepNumber++}</div>
            <div class="step-line"></div>
          </div>
          <section class="step-content">
            <div class="step-card">
              <h2>${heading}</h2>
              ${bodyHtml}
            </div>
          </section>
        </div>
      `;
        });
    }
    // Math questions step
    if (data.questions && Array.isArray(data.questions)) {
        data.questions.forEach((q) => {
            const qLatex = (0, latex_validator_1.validateAndSanitizeLaTeX)(q.question_latex || '').renderedHtml;
            let stepsHtml = '';
            if (q.steps && Array.isArray(q.steps)) {
                q.steps.forEach((s) => {
                    const stepLatex = (0, latex_validator_1.validateAndSanitizeLaTeX)(s.latex || '').renderedHtml;
                    stepsHtml += `
            <div class="step-item">
              <div class="step-explanation">${escapeHtml(s.explanation || '')}</div>
              <div class="math-display">${stepLatex}</div>
            </div>
          `;
                });
            }
            const finalLatex = (0, latex_validator_1.validateAndSanitizeLaTeX)(q.final_answer_latex || '').renderedHtml;
            stepperRowsHtml += `
        <div class="step-row">
          <div class="step-rail">
            <div class="step-marker">${stepNumber++}</div>
            <div class="step-line"></div>
          </div>
          <section class="step-content">
            <div class="step-card">
              <h2>សំណួរទី ${q.number || stepNumber}</h2>
              <div class="math-display">${qLatex}</div>
              <div class="steps-container">${stepsHtml}</div>
              <div class="final-answer-box">
                <div class="label">ចម្លើយចុងក្រោយ / Final Answer</div>
                <div class="math-display">${finalLatex}</div>
              </div>
            </div>
          </section>
        </div>
      `;
        });
    }
    // Warnings step
    if (data.warnings && data.warnings.length > 0) {
        let warnHtml = '';
        data.warnings.forEach((w) => {
            warnHtml += `<div class="step-text">• ${escapeHtml(w)}</div>`;
        });
        stepperRowsHtml += `
      <div class="step-row">
        <div class="step-rail">
          <div class="step-marker">⚠️</div>
          <div class="step-line"></div>
        </div>
        <section class="step-content">
          <div class="warning-box">
            <h3>⚠️ ការប្រុងប្រយ័ត្ន (Security Warning)</h3>
            ${warnHtml}
          </div>
        </section>
      </div>
    `;
    }
    // Recommendations step
    if (data.recommendations && data.recommendations.length > 0) {
        let recHtml = '';
        data.recommendations.forEach((r) => {
            recHtml += `<div class="step-text">• ${escapeHtml(r)}</div>`;
        });
        stepperRowsHtml += `
      <div class="step-row">
        <div class="step-rail">
          <div class="step-marker">💡</div>
          <div class="step-line"></div>
        </div>
        <section class="step-content">
          <div class="recommendation-box">
            <h3>💡 អនុសាសន៍ (Recommendation)</h3>
            ${recHtml}
          </div>
        </section>
      </div>
    `;
    }
    const nowStr = new Date().toLocaleString('en-US', { timeZone: 'Asia/Phnom_Penh' });
    const summaryText = data.summary_km || data.summary || data.title || '';
    templateHtml = templateHtml
        .replace('{{TITLE}}', escapeHtml(data.title || 'Smart AI Assistant'))
        .replace('{{SUMMARY}}', escapeHtml(summaryText))
        .replace('{{TAGS_HTML}}', tagsHtml)
        .replace('{{STEPPER_HTML}}', stepperRowsHtml)
        .replace(/\{\{BOT_NAME\}\}/g, escapeHtml(botName))
        .replace(/\{\{BOT_USERNAME\}\}/g, escapeHtml(botUsername))
        .replace('{{RESPONSE_TYPE_LABEL}}', typeLabels[resType] || '🤖 AI Response')
        .replace('{{GENERATED_AT}}', nowStr);
    return templateHtml;
}
async function renderSolutionToPNG(result, outputPath, botName = 'Smart AI Assistant', botUsername = '@mysmart_v2_2026_bot') {
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
            await page.waitForFunction(() => window.__RENDER_READY__ === true, { timeout: 8000 });
        }
        catch (e) {
            logger_1.logger.warn('Render ready timeout, proceeding to screenshot');
        }
        const cardElement = await page.$('#solution-card');
        if (cardElement) {
            await cardElement.screenshot({ path: outputPath, type: 'png' });
        }
        else {
            await page.screenshot({ path: outputPath, fullPage: true, type: 'png' });
        }
        logger_1.logger.info(`Successfully rendered PNG image to: ${outputPath}`);
        return outputPath;
    }
    finally {
        await context.close();
    }
}
//# sourceMappingURL=image.renderer.js.map