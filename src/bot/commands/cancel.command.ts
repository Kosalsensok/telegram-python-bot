import { Context } from 'telegraf';

export async function handleCancelCommand(ctx: Context) {
  await ctx.reply('❌ បានបោះបង់ប្រតិបត្តិការ។ (Process cancelled)', { parse_mode: 'HTML' });
}
