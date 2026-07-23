"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleHelpCommand = handleHelpCommand;
const khmer_messages_1 = require("../messages/khmer.messages");
const english_messages_1 = require("../messages/english.messages");
async function handleHelpCommand(ctx, userService) {
    const from = ctx.from;
    if (!from)
        return;
    const user = await userService.getOrCreateUser(from.id);
    const msg = user.language === 'km' ? khmer_messages_1.KhmerMessages.help : english_messages_1.EnglishMessages.help;
    await ctx.reply(msg, { parse_mode: 'HTML' });
}
//# sourceMappingURL=help.command.js.map