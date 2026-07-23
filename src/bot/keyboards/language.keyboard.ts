import { Markup } from 'telegraf';

export function getLanguageInlineKeyboard(currentLang: string = 'km') {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback(`${currentLang === 'km' ? '✅ ' : ''}🇰🇭 ភាសាខ្មែរ`, 'set_lang_km'),
      Markup.button.callback(`${currentLang === 'en' ? '✅ ' : ''}🇬🇧 English`, 'set_lang_en'),
    ],
    [Markup.button.callback('⬅️ Main Menu', 'cb_main_menu')],
  ]);
}
