"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.env = void 0;
const dotenv_1 = __importDefault(require("dotenv"));
const zod_1 = require("zod");
dotenv_1.default.config();
const envSchema = zod_1.z.object({
    BOT_TOKEN: zod_1.z.string().default(process.env.BOT_TOKEN || 'dummy_bot_token'),
    BOT_USERNAME: zod_1.z.string().default(process.env.BOT_USERNAME || 'mysmart_v2_2026_bot'),
    AI_PROVIDER: zod_1.z.enum(['openai', 'gemini']).default('gemini'),
    OPENAI_API_KEY: zod_1.z.string().optional(),
    OPENAI_MODEL: zod_1.z.string().default('gpt-4o'),
    GEMINI_API_KEY: zod_1.z.string().default(process.env.GEMINI_API_KEY || 'dummy_gemini_key'),
    GEMINI_MODEL: zod_1.z.string().default('gemini-2.0-flash'),
    DATABASE_URL: zod_1.z.string().default('mysql://root:@127.0.0.1:3306/smart_ai_assistant'),
    APP_URL: zod_1.z.string().default('http://localhost:3000'),
    PORT: zod_1.z.coerce.number().default(3000),
    WEBHOOK_DOMAIN: zod_1.z.string().optional(),
    WEBHOOK_SECRET: zod_1.z.string().optional(),
    MAX_IMAGE_SIZE_MB: zod_1.z.coerce.number().default(10),
    TEMP_DIRECTORY: zod_1.z.string().default('./temp'),
    STORAGE_DRIVER: zod_1.z.enum(['local', 's3']).default('local'),
    STORAGE_PUBLIC_URL: zod_1.z.string().default('http://localhost:3000/public'),
    LOG_LEVEL: zod_1.z.enum(['error', 'warn', 'info', 'debug']).default('info'),
});
const _env = envSchema.safeParse(process.env);
if (!_env.success) {
    console.error('❌ Invalid environment variables:', _env.error.format());
    throw new Error('Invalid configuration');
}
exports.env = _env.data;
//# sourceMappingURL=env.js.map