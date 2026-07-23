"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleGlobalBotError = handleGlobalBotError;
const logger_1 = require("../../utils/logger");
function handleGlobalBotError(err, ctx) {
    logger_1.logger.error(`Unhandled Telegram Bot Error for update ${ctx.update.update_id}:`, err);
    try {
        ctx.reply('⚠️ មានបញ្ហាបច្ចេកទេសក្នុងប្រព័ន្ធ។ (System Error Occurred)').catch(() => { });
    }
    catch (_) { }
}
//# sourceMappingURL=error.handler.js.map