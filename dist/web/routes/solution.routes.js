"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createSolutionRoutes = createSolutionRoutes;
const express_1 = require("express");
const solution_controller_1 = require("../controllers/solution.controller");
function createSolutionRoutes(solutionService) {
    const router = (0, express_1.Router)();
    const controller = new solution_controller_1.SolutionWebController(solutionService);
    router.get('/solution/:publicId', (req, res) => controller.getSolutionPage(req, res));
    return router;
}
//# sourceMappingURL=solution.routes.js.map