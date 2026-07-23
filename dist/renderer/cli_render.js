"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = __importDefault(require("fs"));
const image_renderer_1 = require("./image.renderer");
const pdf_renderer_1 = require("./pdf.renderer");
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
        const raw = fs_1.default.readFileSync(inputPath, 'utf8');
        const payload = JSON.parse(raw);
        if (format === 'pdf') {
            await (0, pdf_renderer_1.renderSolutionToPDF)(payload, outputPath);
        }
        else {
            await (0, image_renderer_1.renderSolutionToPNG)(payload, outputPath);
        }
        console.log(`RENDER_SUCCESS:${outputPath}`);
        process.exit(0);
    }
    catch (err) {
        console.error(`RENDER_ERROR:${err.message}`);
        process.exit(1);
    }
}
runCli();
//# sourceMappingURL=cli_render.js.map