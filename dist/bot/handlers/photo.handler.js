"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handlePhotoUpload = handlePhotoUpload;
const rate_limiter_1 = require("../../utils/rate-limiter");
const khmer_messages_1 = require("../messages/khmer.messages");
const english_messages_1 = require("../messages/english.messages");
const solution_keyboard_1 = require("../keyboards/solution.keyboard");
const logger_1 = require("../../utils/logger");
const env_1 = require("../../config/env");
async function handlePhotoUpload(ctx, telegramFileService, solutionService, userService) {
    const from = ctx.from;
    const message = ctx.message;
    if (!from || !message || !('photo' in message)) {
        return;
    }
    // Rate Limiting check
    if (!(0, rate_limiter_1.checkRateLimit)(from.id, 10, 60)) {
        await ctx.reply(khmer_messages_1.KhmerMessages.rateLimit);
        return;
    }
    const user = await userService.getOrCreateUser(from.id, from.username, from.first_name, from.last_name);
    const langMsgs = user.language === 'km' ? khmer_messages_1.KhmerMessages : english_messages_1.EnglishMessages;
    // Step 1: Send initial progress message
    let statusMessage = await ctx.reply(langMsgs.step1, {
        reply_parameters: { message_id: message.message_id },
    });
    try {
        // Step 2: Edit progress message -> Extracting
        try {
            await ctx.telegram.editMessageText(ctx.chat.id, statusMessage.message_id, undefined, langMsgs.step2);
        }
        catch (_) { }
        // Select highest resolution photo
        const photos = message.photo;
        const highestResPhoto = photos[photos.length - 1];
        // Download photo file from Telegram
        const tempDir = env_1.env.TEMP_DIRECTORY || './temp';
        const downloaded = await telegramFileService.downloadTelegramFile(highestResPhoto.file_id, tempDir);
        // Step 3: Edit progress message -> Solving
        try {
            await ctx.telegram.editMessageText(ctx.chat.id, statusMessage.message_id, undefined, langMsgs.step3);
        }
        catch (_) { }
        // Step 4: Edit progress message -> Rendering Image Card
        try {
            await ctx.telegram.editMessageText(ctx.chat.id, statusMessage.message_id, undefined, langMsgs.step4);
        }
        catch (_) { }
        // Execute math solution pipeline (AI -> KaTeX -> Playwright PNG/PDF -> DB)
        const botUsername = ctx.botInfo?.username ? `@${ctx.botInfo.username}` : `@${env_1.env.BOT_USERNAME}`;
        const solutionOutput = await solutionService.processMathPhoto(from.id, user.telegramId ? 1 : 0, downloaded.buffer, downloaded.mimeType, user.language, user.selectedMode, message.message_id);
        await userService.incrementUserRequests(from.id);
        // Step 5: Delete status message
        try {
            await ctx.telegram.deleteMessage(ctx.chat.id, statusMessage.message_id);
        }
        catch (_) { }
        // Step 6: Reply to original photo with PNG solution image & interactive buttons
        const captionText = langMsgs.captionSuccess(botUsername);
        await ctx.replyWithPhoto({ source: solutionOutput.imagePath }, {
            caption: captionText,
            parse_mode: 'HTML',
            reply_parameters: { message_id: message.message_id },
            ...(0, solution_keyboard_1.getSolutionInlineKeyboard)(solutionOutput.publicId),
        });
    }
    catch (err) {
        logger_1.logger.error(`Error processing math photo for user ${from.id}:`, err);
        try {
            await ctx.telegram.deleteMessage(ctx.chat.id, statusMessage.message_id);
        }
        catch (_) { }
        let errorNotice = langMsgs.aiError;
        if (err.message && err.message.includes('blurry')) {
            errorNotice = langMsgs.blurryImage;
        }
        else if (err.message && err.message.includes('no math')) {
            errorNotice = langMsgs.noProblemDetected;
        }
        await ctx.reply(errorNotice, {
            reply_parameters: { message_id: message.message_id },
        });
    }
}
//# sourceMappingURL=photo.handler.js.map