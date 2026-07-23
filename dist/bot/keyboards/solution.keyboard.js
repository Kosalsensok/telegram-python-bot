"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSolutionInlineKeyboard = getSolutionInlineKeyboard;
const telegraf_1 = require("telegraf");
const env_1 = require("../../config/env");
function getSolutionInlineKeyboard(publicId, appUrl = env_1.env.APP_URL) {
    const webUrl = `${appUrl}/solution/${publicId}`;
    return telegraf_1.Markup.inlineKeyboard([
        [
            telegraf_1.Markup.button.callback('🔄 ដោះស្រាយម្ដងទៀត', `retry_${publicId}`),
            telegraf_1.Markup.button.callback('📥 ទាញយក PDF', `pdf_${publicId}`),
        ],
        [
            telegraf_1.Markup.button.url('🌐 មើលលម្អិត', webUrl),
            telegraf_1.Markup.button.switchToChat('📤 ចែករំលែក', `Check out this math solution: ${webUrl}`),
        ],
        [
            telegraf_1.Markup.button.callback('🏠 ម៉ឺនុយមេ', 'cb_main_menu'),
        ],
    ]);
}
//# sourceMappingURL=solution.keyboard.js.map