"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleStartCommand = handleStartCommand;
const khmer_messages_1 = require("../messages/khmer.messages");
const english_messages_1 = require("../messages/english.messages");
const main_keyboard_1 = require("../keyboards/main.keyboard");
async function handleStartCommand(ctx, userService) {
    const from = ctx.from;
    if (!from)
        return;
    const user = await userService.getOrCreateUser(from.id, from.username, from.first_name, from.last_name);
    const name = from.first_name || 'Friend';
    const msg = user.language === 'km' ? khmer_messages_1.KhmerMessages.welcome(name) : english_messages_1.EnglishMessages.welcome(name);
    await ctx.reply(msg, {
        parse_mode: 'HTML',
        ...(0, main_keyboard_1.getMainReplyKeyboard)(),
    });
}
//# sourceMappingURL=start.command.js.map