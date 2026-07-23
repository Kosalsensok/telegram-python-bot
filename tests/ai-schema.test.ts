import { MathSolutionResultSchema } from '../src/ai/schemas/math-solution.schema';

describe('MathSolutionResultSchema Validation', () => {
  it('should validate a correct math solution JSON payload', () => {
    const validPayload = {
      language: 'km',
      subject: 'mathematics',
      title: 'ដំណោះស្រាយលំហាត់គណិតវិទ្យា',
      questions: [
        {
          number: 1,
          original_question: '(1 - 1/2)(1 - 1/3)...(1 - 1/2024)',
          question_latex: '\\left(1-\\frac{1}{2}\\right)\\left(1-\\frac{1}{3}\\right)',
          steps: [
            {
              explanation: 'បម្លែងកត្តានីមួយៗទៅជាប្រភាគ',
              latex: '= \\frac{1}{2} \\cdot \\frac{2}{3} \\cdot \\frac{3}{4}',
            },
          ],
          final_answer_text: '1/2024',
          final_answer_latex: '\\boxed{\\frac{1}{2024}}',
        },
      ],
      notes: [],
    };

    const parsed = MathSolutionResultSchema.parse(validPayload);
    expect(parsed.questions.length).toBe(1);
    expect(parsed.language).toBe('km');
  });

  it('should reject invalid payloads missing required fields', () => {
    const invalidPayload = {
      language: 'km',
      title: 'Test',
      questions: [],
    };

    expect(() => MathSolutionResultSchema.parse(invalidPayload)).toThrow();
  });
});
