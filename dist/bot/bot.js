"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createTelegramBot = createTelegramBot;
const telegraf_1 = require("telegraf");
const env_1 = require("../config/env");
const start_command_1 = require("./commands/start.command");
const help_command_1 = require("./commands/help.command");
const mode_command_1 = require("./commands/mode.command");
const language_command_1 = require("./commands/language.command");
const history_command_1 = require("./commands/history.command");
const settings_command_1 = require("./commands/settings.command");
const about_command_1 = require("./commands/about.command");
const cancel_command_1 = require("./commands/cancel.command");
const photo_handler_1 = require("./handlers/photo.handler");
const callback_handler_1 = require("./handlers/callback.handler");
const error_handler_1 = require("./handlers/error.handler");
const logger_1 = require("../utils/logger");
function createTelegramBot(userService, telegramFileService, solutionService) {
    const bot = new telegraf_1.Telegraf(env_1.env.BOT_TOKEN);
    // Set command list menu in Telegram client
    bot.telegram.setMyCommands([
        { command: 'start', description: '🚀 Start Bot & Main Menu' },
        { command: 'help', description: '📖 Usage Guide & Support' },
        { command: 'mode', description: '🎯 Select AI Operating Mode' },
        { command: 'language', description: '🌐 Switch Language (Khmer / English)' },
        { command: 'history', description: '📜 View Solution History' },
        { command: 'settings', description: '⚙️ Preferences & Settings' },
        { command: 'about', description: '👤 About Bot Info' },
        { command: 'cancel', description: '❌ Cancel Current Operation' },
    ]).catch((e) => logger_1.logger.warn('Failed setting bot commands:', e));
    // Register commands
    bot.command('start', (ctx) => (0, start_command_1.handleStartCommand)(ctx, userService));
    bot.command('help', (ctx) => (0, help_command_1.handleHelpCommand)(ctx, userService));
    bot.command('mode', (ctx) => (0, mode_command_1.handleModeCommand)(ctx, userService));
    bot.command('language', (ctx) => (0, language_command_1.handleLanguageCommand)(ctx, userService));
    bot.command('history', (ctx) => (0, history_command_1.handleHistoryCommand)(ctx, userService));
    bot.command('settings', (ctx) => (0, settings_command_1.handleSettingsCommand)(ctx, userService));
    bot.command('about', (ctx) => (0, about_command_1.handleAboutCommand)(ctx));
    bot.command('cancel', (ctx) => (0, cancel_command_1.handleCancelCommand)(ctx));
    // Reply Keyboard text triggers
    bot.hears(/🎯 ជ្រើសរើស Mode/, (ctx) => (0, mode_command_1.handleModeCommand)(ctx, userService));
    bot.hears(/📖 ការណែនាំ/, (ctx) => (0, help_command_1.handleHelpCommand)(ctx, userService));
    bot.hears(/🌐 ភាសា/, (ctx) => (0, language_command_1.handleLanguageCommand)(ctx, userService));
    bot.hears(/📜 ប្រវត្តិ/, (ctx) => (0, history_command_1.handleHistoryCommand)(ctx, userService));
    bot.hears(/ℹ️ អំពី Bot/, (ctx) => (0, about_command_1.handleAboutCommand)(ctx));
    bot.hears(/🖼️ វិភាគរូបភាព/, (ctx) => ctx.reply('🖼 សូមផ្ញើរូបភាពលំហាត់គណិតវិទ្យា/សមីការរបស់អ្នកមកកាន់ Bot!'));
    // Photo message handler
    bot.on('photo', (ctx) => (0, photo_handler_1.handlePhotoUpload)(ctx, telegramFileService, solutionService, userService));
    // Callback query handler
    bot.on('callback_query', (ctx) => (0, callback_handler_1.handleCallbackQuery)(ctx, userService, solutionService));
    // Global Error Handler
    bot.catch(error_handler_1.handleGlobalBotError);
    return bot;
}
//# sourceMappingURL=bot.js.map