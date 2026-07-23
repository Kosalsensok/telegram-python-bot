"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const env_1 = require("./config/env");
const prisma_1 = require("./database/prisma");
const logger_1 = require("./utils/logger");
const files_1 = require("./utils/files");
const storage_service_1 = require("./services/storage.service");
const user_service_1 = require("./services/user.service");
const solution_service_1 = require("./services/solution.service");
const telegram_file_service_1 = require("./services/telegram-file.service");
const ai_service_1 = require("./ai/ai.service");
const bot_1 = require("./bot/bot");
const server_1 = require("./web/server");
const image_renderer_1 = require("./renderer/image.renderer");
async function bootstrap() {
    logger_1.logger.info('🚀 Starting Telegram AI Math Solver Bot Application...');
    // 1. Test Database connection
    await (0, prisma_1.testDbConnection)();
    // 2. Instantiate core services
    const storageService = new storage_service_1.StorageService();
    const userService = new user_service_1.UserService();
    const aiService = new ai_service_1.AIService();
    const solutionService = new solution_service_1.SolutionService(aiService, storageService);
    const telegramFileService = new telegram_file_service_1.TelegramFileService(env_1.env.BOT_TOKEN);
    // Periodic temp file cleanup every 30 minutes
    setInterval(() => {
        (0, files_1.cleanOldTempFiles)(env_1.env.TEMP_DIRECTORY || './temp', 60);
    }, 30 * 60 * 1000);
    // 3. Create Telegram Bot instance
    const bot = (0, bot_1.createTelegramBot)(userService, telegramFileService, solutionService);
    // 4. Create Express Web Server
    const app = (0, server_1.createExpressServer)(bot, solutionService);
    const port = env_1.env.PORT || 3000;
    app.listen(port, () => {
        logger_1.logger.info(`🌐 Express web server running on port ${port} [URL: ${env_1.env.APP_URL}]`);
    });
    // 5. Start Bot in Webhook (Production) or Long Polling (Local Dev)
    if (env_1.env.WEBHOOK_DOMAIN && env_1.env.WEBHOOK_SECRET) {
        const webhookUrl = `${env_1.env.WEBHOOK_DOMAIN}/webhook/${env_1.env.WEBHOOK_SECRET}`;
        await bot.telegram.setWebhook(webhookUrl);
        logger_1.logger.info(`🚀 Bot running in Webhook Mode [URL: ${webhookUrl}]`);
    }
    else {
        // Delete any stale webhook and launch Long Polling safely
        try {
            await bot.telegram.deleteWebhook({ drop_pending_updates: true });
            bot.launch(() => {
                logger_1.logger.info(`🚀 Bot running in Long Polling Mode (@${env_1.env.BOT_USERNAME})`);
            }).catch((err) => {
                logger_1.logger.warn(`Telegraf polling warning (e.g. 409 Conflict): ${err.message}`);
            });
        }
        catch (err) {
            logger_1.logger.warn(`Could not start long polling: ${err.message}`);
        }
    }
    // Graceful Shutdown Handler
    const gracefulShutdown = async (signal) => {
        logger_1.logger.info(`Received ${signal}. Shutting down application gracefully...`);
        try {
            bot.stop(signal);
            await (0, image_renderer_1.closeBrowserInstance)();
            logger_1.logger.info('Application shutdown complete.');
            process.exit(0);
        }
        catch (err) {
            logger_1.logger.error('Error during graceful shutdown:', err);
            process.exit(1);
        }
    };
    process.once('SIGINT', () => gracefulShutdown('SIGINT'));
    process.once('SIGTERM', () => gracefulShutdown('SIGTERM'));
}
bootstrap().catch((error) => {
    logger_1.logger.error('Fatal error during application startup:', error);
    process.exit(1);
});
//# sourceMappingURL=index.js.map