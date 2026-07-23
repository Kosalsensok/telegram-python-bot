import { Context } from 'telegraf';
import { TelegramFileService } from '../../services/telegram-file.service';
import { SolutionService } from '../../services/solution.service';
import { UserService } from '../../services/user.service';
import { checkRateLimit } from '../../utils/rate-limiter';
import { KhmerMessages } from '../messages/khmer.messages';
import { EnglishMessages } from '../messages/english.messages';
import { getSolutionInlineKeyboard } from '../keyboards/solution.keyboard';
import { logger } from '../../utils/logger';
import { env } from '../../config/env';

export async function handlePhotoUpload(
  ctx: Context,
  telegramFileService: TelegramFileService,
  solutionService: SolutionService,
  userService: UserService
) {
  const from = ctx.from;
  const message = ctx.message;

  if (!from || !message || !('photo' in message)) {
    return;
  }

  // Rate Limiting check
  if (!checkRateLimit(from.id, 10, 60)) {
    await ctx.reply(KhmerMessages.rateLimit);
    return;
  }

  const user = await userService.getOrCreateUser(
    from.id,
    from.username,
    from.first_name,
    from.last_name
  );

  const langMsgs = user.language === 'km' ? KhmerMessages : EnglishMessages;

  // Step 1: Send initial progress message
  let statusMessage = await ctx.reply(langMsgs.step1, {
    reply_parameters: { message_id: message.message_id },
  });

  try {
    // Step 2: Edit progress message -> Extracting
    try {
      await ctx.telegram.editMessageText(
        ctx.chat!.id,
        statusMessage.message_id,
        undefined,
        langMsgs.step2
      );
    } catch (_) {}

    // Select highest resolution photo
    const photos = message.photo;
    const highestResPhoto = photos[photos.length - 1];

    // Download photo file from Telegram
    const tempDir = env.TEMP_DIRECTORY || './temp';
    const downloaded = await telegramFileService.downloadTelegramFile(highestResPhoto.file_id, tempDir);

    // Step 3: Edit progress message -> Solving
    try {
      await ctx.telegram.editMessageText(
        ctx.chat!.id,
        statusMessage.message_id,
        undefined,
        langMsgs.step3
      );
    } catch (_) {}

    // Step 4: Edit progress message -> Rendering Image Card
    try {
      await ctx.telegram.editMessageText(
        ctx.chat!.id,
        statusMessage.message_id,
        undefined,
        langMsgs.step4
      );
    } catch (_) {}

    // Execute math solution pipeline (AI -> KaTeX -> Playwright PNG/PDF -> DB)
    const botUsername = ctx.botInfo?.username ? `@${ctx.botInfo.username}` : `@${env.BOT_USERNAME}`;

    const solutionOutput = await solutionService.processMathPhoto(
      from.id,
      user.telegramId ? 1 : 0,
      downloaded.buffer,
      downloaded.mimeType,
      user.language,
      user.selectedMode,
      message.message_id
    );

    await userService.incrementUserRequests(from.id);

    // Step 5: Delete status message
    try {
      await ctx.telegram.deleteMessage(ctx.chat!.id, statusMessage.message_id);
    } catch (_) {}

    // Step 6: Reply to original photo with PNG solution image & interactive buttons
    const captionText = langMsgs.captionSuccess(botUsername);

    await ctx.replyWithPhoto(
      { source: solutionOutput.imagePath },
      {
        caption: captionText,
        parse_mode: 'HTML',
        reply_parameters: { message_id: message.message_id },
        ...getSolutionInlineKeyboard(solutionOutput.publicId),
      }
    );

  } catch (err: any) {
    logger.error(`Error processing math photo for user ${from.id}:`, err);
    
    try {
      await ctx.telegram.deleteMessage(ctx.chat!.id, statusMessage.message_id);
    } catch (_) {}

    let errorNotice = langMsgs.aiError;
    if (err.message && err.message.includes('blurry')) {
      errorNotice = langMsgs.blurryImage;
    } else if (err.message && err.message.includes('no math')) {
      errorNotice = langMsgs.noProblemDetected;
    }

    await ctx.reply(errorNotice, {
      reply_parameters: { message_id: message.message_id },
    });
  }
}
