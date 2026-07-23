import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
import { SolutionService } from '../../services/solution.service';
export declare function handleCallbackQuery(ctx: Context, userService: UserService, solutionService: SolutionService): Promise<void>;
