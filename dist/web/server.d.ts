import { Telegraf } from 'telegraf';
import { SolutionService } from '../services/solution.service';
export declare function createExpressServer(bot: Telegraf, solutionService: SolutionService): import("express-serve-static-core").Express;
