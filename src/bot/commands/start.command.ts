import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
import { KhmerMessages } from '../messages/khmer.messages';
import { EnglishMessages } from '../messages/english.messages';
import { getMainReplyKeyboard } from '../keyboards/main.keyboard';

export async function handleStartCommand(ctx: Context, userService: UserService) {
  const from = ctx.from;
  if (!from) return;

  const user = await userService.getOrCreateUser(
    from.id,
    from.username,
    from.first_name,
    from.last_name
  );

  const name = from.first_name || 'Friend';
  const msg = user.language === 'km' ? KhmerMessages.welcome(name) : EnglishMessages.welcome(name);

  await ctx.reply(msg, {
    parse_mode: 'HTML',
    ...getMainReplyKeyboard(),
  });
}
