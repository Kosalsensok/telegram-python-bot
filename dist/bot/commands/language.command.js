"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleLanguageCommand = handleLanguageCommand;
const language_keyboard_1 = require("../keyboards/language.keyboard");
async function handleLanguageCommand(ctx, userService) {
    const from = ctx.from;
    if (!from)
        return;
    const user = await userService.getOrCreateUser(from.id);
    const msg = '🌐 <b>សូមជ្រើសរើសភាសា / Choose Language:</b>';
    await ctx.reply(msg, {
        parse_mode: 'HTML',
        ...(0, language_keyboard_1.getLanguageInlineKeyboard)(user.language),
    });
}
//# sourceMappingURL=language.command.js.map