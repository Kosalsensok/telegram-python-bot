import { Router } from 'express';
import { SolutionWebController } from '../controllers/solution.controller';
import { SolutionService } from '../../services/solution.service';

export function createSolutionRoutes(solutionService: SolutionService): Router {
  const router = Router();
  const controller = new SolutionWebController(solutionService);

  router.get('/solution/:publicId', (req, res) => controller.getSolutionPage(req, res));

  return router;
}
