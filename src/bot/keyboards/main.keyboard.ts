import { Markup } from 'telegraf';

export function getMainReplyKeyboard() {
  return Markup.keyboard([
    ['🎯 ជ្រើសរើស Mode (/mode)', '🖼️ វិភាគរូបភាព'],
    ['📖 ការណែនាំ (/help)', '🌐 ភាសា (/language)'],
    ['📜 ប្រវត្តិ (/history)', 'ℹ️ អំពី Bot (/about)']
  ]).resize().persistent();
}
