import { validateAndSanitizeLaTeX } from '../src/renderer/latex.validator';

describe('LaTeX Validator & Sanitizer', () => {
  it('should validate and render valid LaTeX formulas', () => {
    const input = '\\frac{1}{2024}';
    const result = validateAndSanitizeLaTeX(input);
    expect(result.isValid).toBe(true);
    expect(result.renderedHtml).toContain('katex');
  });

  it('should strip outer delimiters properly', () => {

    const input = '\\[ \\boxed{\\frac{1}{2024}} \\]';

    const result = validateAndSanitizeLaTeX(input);

    expect(result.isValid).toBe(true);

    expect(result.sanitized).not.toContain('\\[');

  });

});
