import katex from 'katex';
import { logger } from '../utils/logger';

export function validateAndSanitizeLaTeX(latexInput: string): { isValid: boolean; sanitized: string; renderedHtml: string } {
  if (!latexInput || !latexInput.trim()) {
    return { isValid: true, sanitized: '', renderedHtml: '' };
  }

  let cleaned = latexInput.trim();
  
  // Strip outer math delimiters if present
  cleaned = cleaned.replace(/^\\\[\s*/, '').replace(/\s*\\\]$/, '');
  cleaned = cleaned.replace(/^\$\$\s*/, '').replace(/\s*\$\$$/, '');
  cleaned = cleaned.replace(/^\$\s*/, '').replace(/\s*\$$/, '');

  try {
    const renderedHtml = katex.renderToString(cleaned, {
      displayMode: true,
      throwOnError: false,
      output: 'html',
    });
    return { isValid: true, sanitized: cleaned, renderedHtml };
  } catch (error) {
    logger.warn(`LaTeX validation error for string "${cleaned}":`, error);
    // Fallback: render plain escaped text inside katex error box
    const fallbackHtml = `<div class="katex-error-box"><code>${escapeHtml(cleaned)}</code></div>`;
    return { isValid: false, sanitized: cleaned, renderedHtml: fallbackHtml };
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
