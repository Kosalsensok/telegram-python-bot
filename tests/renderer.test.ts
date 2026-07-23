import { renderSolutionToPNG, closeBrowserInstance } from '../src/renderer/image.renderer';
import { MathSolutionResult } from '../src/ai/schemas/math-solution.schema';
import path from 'path';
import fs from 'fs';

describe('Solution Image Renderer', () => {
  afterAll(async () => {
    await closeBrowserInstance();
  });

  it('should render a valid MathSolutionResult into a PNG image file', async () => {
    const mockResult: MathSolutionResult = {
      language: 'km',
      subject: 'mathematics',
      title: 'ដំណោះស្រាយលំហាត់គំរូ',
      questions: [
        {
          number: 1,
          original_question: '(1 - 1/2)(1 - 1/3)',
          question_latex: '\\left(1-\\frac{1}{2}\\right)\\left(1-\\frac{1}{3}\\right)',
          steps: [
            {
              explanation: 'សម្រួលប្រភាគ / Simplify fractions',
              latex: '= \\frac{1}{2} \\cdot \\frac{2}{3}',
            },
          ],
          final_answer_text: '1/3',
          final_answer_latex: '\\boxed{\\frac{1}{3}}',
        },
      ],
      notes: [],
    };

    const testOutputPath = path.join(__dirname, 'test_output.png');
    await renderSolutionToPNG(mockResult, testOutputPath);

    expect(fs.existsSync(testOutputPath)).toBe(true);

    // Clean up test file
    if (fs.existsSync(testOutputPath)) {
      fs.unlinkSync(testOutputPath);
    }
  }, 60000);
});
