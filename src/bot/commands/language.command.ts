import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
import { getLanguageInlineKeyboard } from '../keyboards/language.keyboard';

export async function handleLanguageCommand(ctx: Context, userService: UserService) {
  const from = ctx.from;
  if (!from) return;

  const user = await userService.getOrCreateUser(from.id);
  const msg = '🌐 <b>សូមជ្រើសរើសភាសា / Choose Language:</b>';

  await ctx.reply(msg, {
    parse_mode: 'HTML',
    ...getLanguageInlineKeyboard(user.language),
  });
}
