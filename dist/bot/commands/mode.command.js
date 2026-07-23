"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleModeCommand = handleModeCommand;
const mode_keyboard_1 = require("../keyboards/mode.keyboard");
async function handleModeCommand(ctx, userService) {
    const from = ctx.from;
    if (!from)
        return;
    const user = await userService.getOrCreateUser(from.id);
    const msg = user.language === 'km'
        ? '🎯 <b>ជ្រើសរើស AI Operating Mode / Select Operating Mode:</b>'
        : '🎯 <b>Select AI Operating Mode:</b>';
    await ctx.reply(msg, {
        parse_mode: 'HTML',
        ...(0, mode_keyboard_1.getModeInlineKeyboard)(user.selectedMode),
    });
}
//# sourceMappingURL=mode.command.js.map