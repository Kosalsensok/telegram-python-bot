import { Context } from 'telegraf';
import { UserService } from '../../services/user.service';
export declare function handleStartCommand(ctx: Context, userService: UserService): Promise<void>;
