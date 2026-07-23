"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getLanguageInlineKeyboard = getLanguageInlineKeyboard;
const telegraf_1 = require("telegraf");
function getLanguageInlineKeyboard(currentLang = 'km') {
    return telegraf_1.Markup.inlineKeyboard([
        [
            telegraf_1.Markup.button.callback(`${currentLang === 'km' ? '✅ ' : ''}🇰🇭 ភាសាខ្មែរ`, 'set_lang_km'),
            telegraf_1.Markup.button.callback(`${currentLang === 'en' ? '✅ ' : ''}🇬🇧 English`, 'set_lang_en'),
        ],
        [telegraf_1.Markup.button.callback('⬅️ Main Menu', 'cb_main_menu')],
    ]);
}
//# sourceMappingURL=language.keyboard.js.map