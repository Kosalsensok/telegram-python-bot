import { Context } from 'telegraf';
import { logger } from '../../utils/logger';

export function handleGlobalBotError(err: unknown, ctx: Context) {
  logger.error(`Unhandled Telegram Bot Error for update ${ctx.update.update_id}:`, err);
  try {
    ctx.reply('⚠️ មានបញ្ហាបច្ចេកទេសក្នុងប្រព័ន្ធ។ (System Error Occurred)').catch(() => {});
  } catch (_) {}
}
