import { Context } from 'telegraf';
import { env } from '../../config/env';

export async function handleAboutCommand(ctx: Context) {
  const msg = (
    `👤 <b>អំពី Smart AI Math Solver Bot / About</b>\n\n` +
    `🤖 <b>Bot Name:</b> Smart AI Math Solver\n` +
    `⚡ <b>Engine:</b> KaTeX + Playwright + ${env.AI_PROVIDER.toUpperCase()}\n` +
    `📐 <b>Rendering:</b> High-Res PNG Card & A4 PDF Document\n` +
    `🌐 <b>Languages:</b> Khmer & English\n\n` +
    `🔒 <b>Privacy:</b> Secure temporary image rendering in memory.`
  );

  await ctx.reply(msg, { parse_mode: 'HTML' });
}
