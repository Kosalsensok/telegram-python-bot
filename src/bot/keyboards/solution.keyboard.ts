import { Markup } from 'telegraf';
import { env } from '../../config/env';

export function getSolutionInlineKeyboard(publicId: string, appUrl: string = env.APP_URL) {
  const webUrl = `${appUrl}/solution/${publicId}`;

  return Markup.inlineKeyboard([
    [
      Markup.button.callback('🔄 ដោះស្រាយម្ដងទៀត', `retry_${publicId}`),
      Markup.button.callback('📥 ទាញយក PDF', `pdf_${publicId}`),
    ],
    [
      Markup.button.url('🌐 មើលលម្អិត', webUrl),
      Markup.button.switchToChat('📤 ចែករំលែក', `Check out this math solution: ${webUrl}`),
    ],
    [
      Markup.button.callback('🏠 ម៉ឺនុយមេ', 'cb_main_menu'),
    ],
  ]);
}
