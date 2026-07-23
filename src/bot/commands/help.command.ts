import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
import { KhmerMessages } from '../messages/khmer.messages';
import { EnglishMessages } from '../messages/english.messages';

export async function handleHelpCommand(ctx: Context, userService: UserService) {
  const from = ctx.from;
  if (!from) return;

  const user = await userService.getOrCreateUser(from.id);
  const msg = user.language === 'km' ? KhmerMessages.help : EnglishMessages.help;

  await ctx.reply(msg, { parse_mode: 'HTML' });
}
