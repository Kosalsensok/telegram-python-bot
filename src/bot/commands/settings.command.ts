import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';

export async function handleSettingsCommand(ctx: Context, userService: UserService) {
  const from = ctx.from;
  if (!from) return;

  const user = await userService.getOrCreateUser(from.id);
  const msg = (
    `⚙️ <b>ការកំណត់ផ្ទាល់ខ្លួន (Settings)</b>\n\n` +
    `🌐 <b>Language:</b> ${user.language === 'km' ? 'ភាសាខ្មែរ (Khmer)' : 'English'}\n` +
    `🎯 <b>Active Mode:</b> <code>${user.selectedMode.toUpperCase()}</code>\n` +
    `📊 <b>Total Requests:</b> ${user.totalRequests}\n\n` +
    `👉 ប្រើប្រាស់បញ្ជា /language ឬ /mode ដើម្បីកែប្រែការកំណត់។`
  );

  await ctx.reply(msg, { parse_mode: 'HTML' });
}
