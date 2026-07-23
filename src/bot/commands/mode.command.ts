import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
import { getModeInlineKeyboard } from '../keyboards/mode.keyboard';

export async function handleModeCommand(ctx: Context, userService: UserService) {
  const from = ctx.from;
  if (!from) return;

  const user = await userService.getOrCreateUser(from.id);
  const msg = user.language === 'km'
    ? '🎯 <b>ជ្រើសរើស AI Operating Mode / Select Operating Mode:</b>'
    : '🎯 <b>Select AI Operating Mode:</b>';

  await ctx.reply(msg, {
    parse_mode: 'HTML',
    ...getModeInlineKeyboard(user.selectedMode),
  });
}
