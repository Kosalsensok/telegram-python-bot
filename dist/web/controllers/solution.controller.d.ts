import { Request, Response } from 'express';
import { SolutionService } from '../../services/solution.service';
export declare class SolutionWebController {
    private solutionService;
    constructor(solutionService: SolutionService);
    getHomePage(req: Request, res: Response): Promise<void>;
    getSolutionPage(req: Request, res: Response): Promise<Response<any, Record<string, any>> | undefined>;
}
