import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
export declare function handleHistoryCommand(ctx: Context, userService: UserService): Promise<void>;
