import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
export declare function handleHelpCommand(ctx: Context, userService: UserService): Promise<void>;
