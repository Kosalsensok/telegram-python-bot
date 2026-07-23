import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
import { SolutionService } from '../../services/solution.service';
import { getModeInlineKeyboard } from '../keyboards/mode.keyboard';
import { getLanguageInlineKeyboard } from '../keyboards/language.keyboard';
import { KhmerMessages } from '../messages/khmer.messages';
import { EnglishMessages } from '../messages/english.messages';
import { logger } from '../../utils/logger';
import path from 'path';
import fs from 'fs';
import { env } from '../../config/env';

export async function handleCallbackQuery(
  ctx: Context,
  userService: UserService,
  solutionService: SolutionService
) {
  if (!ctx.callbackQuery || !('data' in ctx.callbackQuery)) return;

  const data = ctx.callbackQuery.data;
  const from = ctx.from;
  if (!from) return;

  try {
    const user = await userService.getOrCreateUser(from.id);

    // 1. PDF Download callback (pdf_{publicId})
    if (data.startsWith('pdf_')) {
      const publicId = data.replace('pdf_', '');
      await ctx.answerCbQuery('📥 កំពុងរៀបចំ PDF... / Preparing PDF...');

      const solutionRecord = await solutionService.getSolutionByPublicId(publicId);
      const pdfPath = solutionRecord?.outputPdfPath || path.join(env.TEMP_DIRECTORY || './temp', `math-solution-${publicId}.pdf`);

      if (fs.existsSync(pdfPath)) {
        await ctx.replyWithDocument(
          { source: pdfPath, filename: `math-solution-${publicId}.pdf` },
          { caption: '📄 <b>PDF Solution Document</b>', parse_mode: 'HTML' }
        );
      } else {
        await ctx.reply('⚠️ PDF file is expired or unavailable.');
      }
      return;
    }

    // 2. Retry callback (retry_{publicId})
    if (data.startsWith('retry_')) {
      await ctx.answerCbQuery('🔄 សូមផ្ញើរូបភាពលំហាត់ម្ដងទៀត / Please resend photo');
      await ctx.reply('🖼 <b>សូមផ្ញើរូបភាពលំហាត់មកកាន់ Bot ម្ដងទៀត៖</b>', { parse_mode: 'HTML' });
      return;
    }

    // 3. Set Mode callback (set_mode_{modeKey})
    if (data.startsWith('set_mode_')) {
      const selectedMode = data.replace('set_mode_', '');
      await userService.setUserMode(from.id, selectedMode);
      await ctx.answerCbQuery(`✅ Active Mode: ${selectedMode.toUpperCase()}`);

      const msg = user.language === 'km'
        ? `✅ <b>បានកំណត់ Mode៖ ${selectedMode.toUpperCase()}</b>`
        : `✅ <b>Mode set to: ${selectedMode.toUpperCase()}</b>`;

      await ctx.editMessageText(msg, {
        parse_mode: 'HTML',
        ...getModeInlineKeyboard(selectedMode),
      });
      return;
    }

    // 4. Set Language callback (set_lang_{langKey})
    if (data.startsWith('set_lang_')) {
      const selectedLang = data.replace('set_lang_', '') as 'km' | 'en';
      await userService.setUserLanguage(from.id, selectedLang);
      await ctx.answerCbQuery(`✅ Language: ${selectedLang === 'km' ? 'ភាសាខ្មែរ' : 'English'}`);

      const msg = selectedLang === 'km'
        ? '🇰🇭 <b>ភាសាត្រូវបានកំណត់ជា៖ ភាសាខ្មែរ (Khmer)</b>'
        : '🇬🇧 <b>Language set to: English</b>';

      await ctx.editMessageText(msg, {
        parse_mode: 'HTML',
        ...getLanguageInlineKeyboard(selectedLang),
      });
      return;
    }

    // 5. Main Menu Callback
    if (data === 'cb_main_menu') {
      await ctx.answerCbQuery();
      const name = from.first_name || 'Friend';
      const msg = user.language === 'km' ? KhmerMessages.welcome(name) : EnglishMessages.welcome(name);
      await ctx.reply(msg, { parse_mode: 'HTML' });
      return;
    }

  } catch (err) {
    logger.error('Callback handler error:', err);
    try {
      await ctx.answerCbQuery('Error processing request.');
    } catch (_) {}
  }
}
