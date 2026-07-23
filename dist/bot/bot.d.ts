import { Telegraf } from 'telegraf';
import { UserService } from '../services/user.service';
import { TelegramFileService } from '../services/telegram-file.service';
import { SolutionService } from '../services/solution.service';
export declare function createTelegramBot(userService: UserService, telegramFileService: TelegramFileService, solutionService: SolutionService): Telegraf;
