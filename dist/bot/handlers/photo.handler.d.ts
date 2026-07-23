import { Context } from 'telegraf';
import { TelegramFileService } from '../../services/telegram-file.service';
import { SolutionService } from '../../services/solution.service';
import { UserService } from '../../services/user.service';
export declare function handlePhotoUpload(ctx: Context, telegramFileService: TelegramFileService, solutionService: SolutionService, userService: UserService): Promise<void>;
