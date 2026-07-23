"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getModeInlineKeyboard = getModeInlineKeyboard;
const telegraf_1 = require("telegraf");
function getModeInlineKeyboard(currentMode = 'standard') {
    const modes = [
        { key: 'standard', label: '📐 Standard Math' },
        { key: 'khmer_math', label: '🇰🇭 Khmer Math' },
        { key: 'detailed', label: '🧮 Detailed Solution' },
        { key: 'quick', label: '⚡ Quick Answer' },
        { key: 'chemistry', label: '⚗️ Chemistry' },
        { key: 'physics', label: '🔭 Physics' },
        { key: 'table', label: '📊 Table and Formula' },
    ];
    const buttons = modes.map((m) => {
        const prefix = m.key === currentMode ? '✅ ' : '';
        return [telegraf_1.Markup.button.callback(`${prefix}${m.label}`, `set_mode_${m.key}`)];
    });
    buttons.push([telegraf_1.Markup.button.callback('⬅️ Main Menu', 'cb_main_menu')]);
    return telegraf_1.Markup.inlineKeyboard(buttons);
}
//# sourceMappingURL=mode.keyboard.js.map