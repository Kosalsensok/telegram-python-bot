import dotenv from 'dotenv';
import path from 'path';
import { z } from 'zod';

dotenv.config();

const envSchema = z.object({
  BOT_TOKEN: z.string().min(1, 'BOT_TOKEN is required'),
  BOT_USERNAME: z.string().default('mysmart_v2_2026_bot'),

  AI_PROVIDER: z.enum(['openai', 'gemini']).default('gemini'),
  OPENAI_API_KEY: z.string().optional(),
  OPENAI_MODEL: z.string().default('gpt-4o'),

  GEMINI_API_KEY: z.string().optional(),
  GEMINI_MODEL: z.string().default('gemini-2.0-flash'),

  DATABASE_URL: z.string().default('mysql://root:@127.0.0.1:3306/smart_ai_assistant'),

  APP_URL: z.string().default('http://localhost:3000'),
  PORT: z.coerce.number().default(3000),

  WEBHOOK_DOMAIN: z.string().optional(),
  WEBHOOK_SECRET: z.string().optional(),

  MAX_IMAGE_SIZE_MB: z.coerce.number().default(10),
  TEMP_DIRECTORY: z.string().default('./temp'),
  STORAGE_DRIVER: z.enum(['local', 's3']).default('local'),
  STORAGE_PUBLIC_URL: z.string().default('http://localhost:3000/public'),

  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('info'),
});

const _env = envSchema.safeParse(process.env);

if (!_env.success) {
  console.error('❌ Invalid environment variables:', _env.error.format());
  throw new Error('Invalid configuration');
}

export const env = _env.data;
