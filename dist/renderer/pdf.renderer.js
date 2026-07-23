"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.renderSolutionToPDF = renderSolutionToPDF;
const playwright_1 = __importDefault(require("playwright"));
const image_renderer_1 = require("./image.renderer");
const logger_1 = require("../utils/logger");
async function renderSolutionToPDF(result, outputPath, botName = 'Smart AI Assistant', botUsername = '@mysmart_v2_2026_bot') {
    const htmlContent = (0, image_renderer_1.buildSolutionHtml)(result, botName, botUsername);
    const browser = await playwright_1.default.chromium.launch({
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
            await page.waitForFunction(() => window.__RENDER_READY__ === true, { timeout: 8000 });
        }
        catch (e) {
            logger_1.logger.warn('Render ready timeout for PDF, proceeding');
        }
        await page.pdf({
            path: outputPath,
            format: 'A4',
            margin: { top: '15mm', bottom: '15mm', left: '15mm', right: '15mm' },
            printBackground: true,
        });
        logger_1.logger.info(`Successfully generated solution PDF document to: ${outputPath}`);
        return outputPath;
    }
    finally {
        await page.close();
        await browser.close();
    }
}
//# sourceMappingURL=pdf.renderer.js.map