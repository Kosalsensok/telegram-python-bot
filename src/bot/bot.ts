import { Telegraf } from 'telegraf';
import { env } from '../config/env';
import { UserService } from '../services/user.service';
import { TelegramFileService } from '../services/telegram-file.service';
import { SolutionService } from '../services/solution.service';

import { handleStartCommand } from './commands/start.command';
import { handleHelpCommand } from './commands/help.command';
import { handleModeCommand } from './commands/mode.command';
import { handleLanguageCommand } from './commands/language.command';
import { handleHistoryCommand } from './commands/history.command';
import { handleSettingsCommand } from './commands/settings.command';
import { handleAboutCommand } from './commands/about.command';
import { handleCancelCommand } from './commands/cancel.command';

import { handlePhotoUpload } from './handlers/photo.handler';
import { handleCallbackQuery } from './handlers/callback.handler';
import { handleGlobalBotError } from './handlers/error.handler';
import { logger } from '../utils/logger';

export function createTelegramBot(
  userService: UserService,
  telegramFileService: TelegramFileService,
  solutionService: SolutionService
): Telegraf {
  const bot = new Telegraf(env.BOT_TOKEN);

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
  ]).catch((e) => logger.warn('Failed setting bot commands:', e));

  // Register commands
  bot.command('start', (ctx) => handleStartCommand(ctx, userService));
  bot.command('help', (ctx) => handleHelpCommand(ctx, userService));
  bot.command('mode', (ctx) => handleModeCommand(ctx, userService));
  bot.command('language', (ctx) => handleLanguageCommand(ctx, userService));
  bot.command('history', (ctx) => handleHistoryCommand(ctx, userService));
  bot.command('settings', (ctx) => handleSettingsCommand(ctx, userService));
  bot.command('about', (ctx) => handleAboutCommand(ctx));
  bot.command('cancel', (ctx) => handleCancelCommand(ctx));

  // Reply Keyboard text triggers
  bot.hears(/🎯 ជ្រើសរើស Mode/, (ctx) => handleModeCommand(ctx, userService));
  bot.hears(/📖 ការណែនាំ/, (ctx) => handleHelpCommand(ctx, userService));
  bot.hears(/🌐 ភាសា/, (ctx) => handleLanguageCommand(ctx, userService));
  bot.hears(/📜 ប្រវត្តិ/, (ctx) => handleHistoryCommand(ctx, userService));
  bot.hears(/ℹ️ អំពី Bot/, (ctx) => handleAboutCommand(ctx));
  bot.hears(/🖼️ វិភាគរូបភាព/, (ctx) => ctx.reply('🖼 សូមផ្ញើរូបភាពលំហាត់គណិតវិទ្យា/សមីការរបស់អ្នកមកកាន់ Bot!'));

  // Photo message handler
  bot.on('photo', (ctx) => handlePhotoUpload(ctx, telegramFileService, solutionService, userService));

  // Callback query handler
  bot.on('callback_query', (ctx) => handleCallbackQuery(ctx, userService, solutionService));

  // Global Error Handler
  bot.catch(handleGlobalBotError);

  return bot;
}
