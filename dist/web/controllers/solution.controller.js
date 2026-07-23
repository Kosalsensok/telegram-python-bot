"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SolutionWebController = void 0;
const env_1 = require("../../config/env");
const solution_view_template_1 = require("../templates/solution-view.template");
const landing_page_template_1 = require("../templates/landing-page.template");
const not_found_template_1 = require("../templates/not-found.template");
class SolutionWebController {
    solutionService;
    constructor(solutionService) {
        this.solutionService = solutionService;
    }
    async getHomePage(req, res) {
        const htmlPage = (0, landing_page_template_1.renderLandingPageHtml)(env_1.env.APP_URL, env_1.env.BOT_USERNAME);
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.send(htmlPage);
    }
    async getSolutionPage(req, res) {
        const publicId = req.params.publicId;
        const solution = await this.solutionService.getSolutionByPublicId(publicId);
        if (!solution || (!solution.structuredResult && !solution.questions)) {
            const notFoundPage = (0, not_found_template_1.renderNotFoundHtml)(publicId, env_1.env.BOT_USERNAME);
            res.setHeader('Content-Type', 'text/html; charset=utf-8');
            return res.status(404).send(notFoundPage);
        }
        const htmlPage = (0, solution_view_template_1.renderSolutionViewHtml)(solution, publicId, env_1.env.APP_URL, env_1.env.BOT_USERNAME);
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.send(htmlPage);
    }
}
exports.SolutionWebController = SolutionWebController;
//# sourceMappingURL=solution.controller.js.map