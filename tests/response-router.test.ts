import {
  containsBrokenCharacters,
  cleanBrokenCharacters,
  StructuredSolutionSchema,
} from '../src/ai/schemas/response-type.schema';
import { buildSolutionHtml, renderSolutionToPNG, closeBrowserInstance } from '../src/renderer/image.renderer';
import path from 'path';
import fs from 'fs';

describe('Response Type Router & Renderer Tests', () => {
  afterAll(async () => {
    await closeBrowserInstance();
  });

  test('1. Detects broken characters (□ and replacement glyphs)', () => {
    expect(containsBrokenCharacters('\u25A1 Hello World')).toBe(true);
    expect(containsBrokenCharacters('\uFFFD Invalid character')).toBe(true);
    expect(containsBrokenCharacters('Normal Khmer text ជំរាបសួរ')).toBe(false);
  });

  test('2. Cleans broken characters cleanly', () => {
    const dirty = '\u25A1 Section 1: \u25A1 Important note \uFFFD';
    const cleaned = cleanBrokenCharacters(dirty);
    expect(cleaned).not.toContain('\u25A1');
    expect(cleaned).not.toContain('\uFFFD');
    expect(cleaned).toContain('• Section 1: • Important note');
  });

  test('3. Cursor Payment Email Visual Fixture Test', async () => {
    const fixturePayload = {
      response_type: 'email' as const,
      language: 'km',
      title: 'ការវិភាគអ៊ីមែល៖ Payment to Cursor was unsuccessful',
      summary: 'ការបង់ប្រាក់ចំនួន $41,869.47 ទៅ Cursor មិនបានជោគជ័យ។',
      key_values: [
        { label: 'ប្រធានបទ', value: '$41,869.47 payment to Cursor was unsuccessful' },
        { label: 'អ្នកផ្ញើ', value: 'Cursor <failed-payments+acct...@stripe.com>' },
        { label: 'កាត', value: 'Visa ending in 2079' },
        { label: 'ចំនួនទឹកប្រាក់', value: '$41,869.47' },
      ],
      sections: [
        {
          heading: 'ខ្លឹមសារអ៊ីមែល',
          content:
            'We attempted to charge your Visa ending in 2079 for your Cursor subscription again, but were unsuccessful.',
        },
      ],
      warnings: [
        'កុំចុចតំណភ្ជាប់ភ្លាមៗ។ ពិនិត្យ domain និងចូលគណនីតាម Website ផ្លូវការរបស់ Cursor ដោយផ្ទាល់។',
      ],
      recommendations: ['ពិនិត្យ Billing និង Payment Method ក្នុងគណនីផ្លូវការ។'],
      math_expressions: [],
    };

    // Validate Zod Schema
    const parsed = StructuredSolutionSchema.parse(fixturePayload);
    expect(parsed.response_type).toBe('email');

    // Build HTML
    const html = buildSolutionHtml(parsed);
    expect(html).not.toContain('\u25A1');
    expect(html).toContain('$41,869.47');

    // Render PNG file
    const outPng = path.join(__dirname, 'test_email_fixture.png');
    await renderSolutionToPNG(parsed, outPng);
    expect(fs.existsSync(outPng)).toBe(true);
  }, 60000);
});
