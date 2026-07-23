"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleCancelCommand = handleCancelCommand;
async function handleCancelCommand(ctx) {
    await ctx.reply('❌ បានបោះបង់ប្រតិបត្តិការ។ (Process cancelled)', { parse_mode: 'HTML' });
}
//# sourceMappingURL=cancel.command.js.map