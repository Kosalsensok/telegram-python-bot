import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
export declare function handleSettingsCommand(ctx: Context, userService: UserService): Promise<void>;
