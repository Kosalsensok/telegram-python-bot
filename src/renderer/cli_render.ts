import fs from 'fs';
import path from 'path';
import { renderSolutionToPNG } from './image.renderer';
import { renderSolutionToPDF } from './pdf.renderer';

async function runCli() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: node cli_render.js <input_json_path> <output_file_path> [format: png|pdf]');
    process.exit(1);
  }

  const inputPath = args[0];
  const outputPath = args[1];
  const format = args[2] || (outputPath.endsWith('.pdf') ? 'pdf' : 'png');

  try {
    const raw = fs.readFileSync(inputPath, 'utf8');
    const payload = JSON.parse(raw);

    if (format === 'pdf') {
      await renderSolutionToPDF(payload, outputPath);
    } else {
      await renderSolutionToPNG(payload, outputPath);
    }

    console.log(`RENDER_SUCCESS:${outputPath}`);
    process.exit(0);
  } catch (err: any) {
    console.error(`RENDER_ERROR:${err.message}`);
    process.exit(1);
  }
}

runCli();
