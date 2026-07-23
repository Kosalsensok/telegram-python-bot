import { Request, Response } from 'express';
import { SolutionService } from '../../services/solution.service';
import { env } from '../../config/env';
import { renderSolutionViewHtml } from '../templates/solution-view.template';
import { renderLandingPageHtml } from '../templates/landing-page.template';
import { renderNotFoundHtml } from '../templates/not-found.template';

export class SolutionWebController {
  private solutionService: SolutionService;

  constructor(solutionService: SolutionService) {
    this.solutionService = solutionService;
  }

  async getHomePage(req: Request, res: Response) {
    const htmlPage = renderLandingPageHtml(env.APP_URL, env.BOT_USERNAME);
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.send(htmlPage);
  }

  async getSolutionPage(req: Request, res: Response) {
    const publicId = req.params.publicId;
    const solution = await this.solutionService.getSolutionByPublicId(publicId);

    if (!solution || (!solution.structuredResult && !solution.questions)) {
      const notFoundPage = renderNotFoundHtml(publicId, env.BOT_USERNAME);
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      return res.status(404).send(notFoundPage);
    }

    const htmlPage = renderSolutionViewHtml(solution, publicId, env.APP_URL, env.BOT_USERNAME);
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.send(htmlPage);
  }
}
