"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getMainReplyKeyboard = getMainReplyKeyboard;
const telegraf_1 = require("telegraf");
function getMainReplyKeyboard() {
    return telegraf_1.Markup.keyboard([
        ['🎯 ជ្រើសរើស Mode (/mode)', '🖼️ វិភាគរូបភាព'],
        ['📖 ការណែនាំ (/help)', '🌐 ភាសា (/language)'],
        ['📜 ប្រវត្តិ (/history)', 'ℹ️ អំពី Bot (/about)']
    ]).resize().persistent();
}
//# sourceMappingURL=main.keyboard.js.map