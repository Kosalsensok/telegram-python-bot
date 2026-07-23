import express from 'express';
import path from 'path';
import { Telegraf } from 'telegraf';
import { env } from '../config/env';
import { SolutionService } from '../services/solution.service';
import { createSolutionRoutes } from './routes/solution.routes';
import { logger } from '../utils/logger';

export function createExpressServer(bot: Telegraf, solutionService: SolutionService) {
  const app = express();

  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Static directory for temp public file downloads
  const publicDir = path.resolve(env.TEMP_DIRECTORY || './temp');
  app.use('/public', express.static(publicDir));

  // Home route redirecting to Demo Solution Page
  app.get('/', (req, res) => {
    res.redirect('/solution/demo123');
  });

  // Health Check Endpoint
  app.get('/health', (req, res) => {
    res.json({
      status: 'ok',
      service: 'Telegram AI Math Solver Bot',
      timestamp: new Date().toISOString(),
      env: process.env.NODE_ENV || 'development',
    });
  });

  // Web solution pages
  app.use('/', createSolutionRoutes(solutionService));

  // Production Telegram Webhook endpoint support
  if (env.WEBHOOK_DOMAIN && env.WEBHOOK_SECRET) {
    const webhookPath = `/webhook/${env.WEBHOOK_SECRET}`;
    app.use(bot.webhookCallback(webhookPath));
    logger.info(`Registered Telegram Webhook route at: ${webhookPath}`);
  }

  return app;
}
