import { Markup } from 'telegraf';

export function getModeInlineKeyboard(currentMode: string = 'standard') {
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
    return [Markup.button.callback(`${prefix}${m.label}`, `set_mode_${m.key}`)];
  });

  buttons.push([Markup.button.callback('⬅️ Main Menu', 'cb_main_menu')]);

  return Markup.inlineKeyboard(buttons);
}
