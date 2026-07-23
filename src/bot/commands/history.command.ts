import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
import { getPrismaClient, isDatabaseConnected } from '../../database/prisma';

export async function handleHistoryCommand(ctx: Context, userService: UserService) {
  const from = ctx.from;
  if (!from) return;

  await userService.getOrCreateUser(from.id);
  const prisma = getPrismaClient();

  if (!isDatabaseConnected() || !prisma) {
    await ctx.reply('⚠️ មូលដ្ឋានទិន្នន័យមិនដំណើរការជាបណ្ដោះអាសន្ន។ / Database is temporarily unavailable.');
    return;
  }

  try {
    const dbUser = await prisma.user.findUnique({
      where: { telegramId: BigInt(from.id) },
    });

    if (!dbUser) {
      await ctx.reply('ℹ️ មិនទាន់មានប្រវត្តិប្រើប្រាស់ទេ។ / No usage history found.');
      return;
    }

    const recentSolutions = await prisma.solution.findMany({
      where: { userId: dbUser.id, status: 'COMPLETED' },
      orderBy: { createdAt: 'desc' },
      take: 5,
    });

    if (recentSolutions.length === 0) {
      await ctx.reply('ℹ️ មិនទាន់មានប្រវត្តិដោះស្រាយលំហាត់ទេ។ / No recent solutions found.');
      return;
    }

    let msg = '📜 <b>ប្រវត្តិដោះស្រាយលំហាត់ចុងក្រោយ (Recent Solutions):</b>\n\n';
    recentSolutions.forEach((sol, i) => {
      const title = sol.subject.toUpperCase();
      const dateStr = new Date(sol.createdAt).toLocaleDateString('km-KH');
      msg += `${i + 1}. <b>${title}</b> (${dateStr})\n👉 <a href="${process.env.APP_URL}/solution/${sol.publicId}">មើលចម្លើយពេញលេញ (View Solution)</a>\n\n`;
    });

    await ctx.reply(msg, { parse_mode: 'HTML', link_preview_options: { is_disabled: true } });
  } catch (_err) {
    await ctx.reply('⚠️ មានបញ្ហាក្នុងការទាញយកប្រវត្តិ។ / Failed to retrieve history.');
  }
}
