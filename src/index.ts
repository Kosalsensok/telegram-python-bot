import { env } from './config/env';
import { testDbConnection } from './database/prisma';
import { logger } from './utils/logger';
import { cleanOldTempFiles } from './utils/files';

import { StorageService } from './services/storage.service';
import { UserService } from './services/user.service';
import { SolutionService } from './services/solution.service';
import { TelegramFileService } from './services/telegram-file.service';
import { AIService } from './ai/ai.service';

import { createTelegramBot } from './bot/bot';
import { createExpressServer } from './web/server';
import { closeBrowserInstance } from './renderer/image.renderer';

async function bootstrap() {
  logger.info('🚀 Starting Telegram AI Math Solver Bot Application...');

  // 1. Test Database connection
  await testDbConnection();

  // 2. Instantiate core services
  const storageService = new StorageService();
  const userService = new UserService();
  const aiService = new AIService();
  const solutionService = new SolutionService(aiService, storageService);
  const telegramFileService = new TelegramFileService(env.BOT_TOKEN);

  // Periodic temp file cleanup every 30 minutes
  setInterval(() => {
    cleanOldTempFiles(env.TEMP_DIRECTORY || './temp', 60);
  }, 30 * 60 * 1000);

  // 3. Create Telegram Bot instance
  const bot = createTelegramBot(userService, telegramFileService, solutionService);

  // 4. Create Express Web Server
  const app = createExpressServer(bot, solutionService);
  const port = env.PORT || 3000;

  app.listen(port, () => {
    logger.info(`🌐 Express web server running on port ${port} [URL: ${env.APP_URL}]`);
  });

  // 5. Start Bot in Webhook (Production) or Long Polling (Local Dev)
  if (env.WEBHOOK_DOMAIN && env.WEBHOOK_SECRET) {
    const webhookUrl = `${env.WEBHOOK_DOMAIN}/webhook/${env.WEBHOOK_SECRET}`;
    await bot.telegram.setWebhook(webhookUrl);
    logger.info(`🚀 Bot running in Webhook Mode [URL: ${webhookUrl}]`);
  } else {
    // Delete any stale webhook and launch Long Polling safely
    try {
      await bot.telegram.deleteWebhook({ drop_pending_updates: true });
      bot.launch(() => {
        logger.info(`🚀 Bot running in Long Polling Mode (@${env.BOT_USERNAME})`);
      }).catch((err) => {
        logger.warn(`Telegraf polling warning (e.g. 409 Conflict): ${err.message}`);
      });
    } catch (err: any) {
      logger.warn(`Could not start long polling: ${err.message}`);
    }
  }

  // Graceful Shutdown Handler
  const gracefulShutdown = async (signal: string) => {
    logger.info(`Received ${signal}. Shutting down application gracefully...`);
    try {
      bot.stop(signal);
      await closeBrowserInstance();
      logger.info('Application shutdown complete.');
      process.exit(0);
    } catch (err) {
      logger.error('Error during graceful shutdown:', err);
      process.exit(1);
    }
  };

  process.once('SIGINT', () => gracefulShutdown('SIGINT'));
  process.once('SIGTERM', () => gracefulShutdown('SIGTERM'));
}

bootstrap().catch((error) => {
  logger.error('Fatal error during application startup:', error);
  process.exit(1);
});
