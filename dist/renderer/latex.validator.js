"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateAndSanitizeLaTeX = validateAndSanitizeLaTeX;
const katex_1 = __importDefault(require("katex"));
const logger_1 = require("../utils/logger");
function validateAndSanitizeLaTeX(latexInput) {
    if (!latexInput || !latexInput.trim()) {
        return { isValid: true, sanitized: '', renderedHtml: '' };
    }
    let cleaned = latexInput.trim();
    // Strip outer math delimiters if present
    cleaned = cleaned.replace(/^\\\[\s*/, '').replace(/\s*\\\]$/, '');
    cleaned = cleaned.replace(/^\$\$\s*/, '').replace(/\s*\$\$$/, '');
    cleaned = cleaned.replace(/^\$\s*/, '').replace(/\s*\$$/, '');
    try {
        const renderedHtml = katex_1.default.renderToString(cleaned, {
            displayMode: true,
            throwOnError: false,
            output: 'html',
        });
        return { isValid: true, sanitized: cleaned, renderedHtml };
    }
    catch (error) {
        logger_1.logger.warn(`LaTeX validation error for string "${cleaned}":`, error);
        // Fallback: render plain escaped text inside katex error box
        const fallbackHtml = `<div class="katex-error-box"><code>${escapeHtml(cleaned)}</code></div>`;
        return { isValid: false, sanitized: cleaned, renderedHtml: fallbackHtml };
    }
}
function escapeHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
//# sourceMappingURL=latex.validator.js.map