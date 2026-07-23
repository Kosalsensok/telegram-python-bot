"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createExpressServer = createExpressServer;
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const env_1 = require("../config/env");
const solution_routes_1 = require("./routes/solution.routes");
const logger_1 = require("../utils/logger");
function createExpressServer(bot, solutionService) {
    const app = (0, express_1.default)();
    app.use(express_1.default.json());
    app.use(express_1.default.urlencoded({ extended: true }));
    // Static directory for temp public file downloads
    const publicDir = path_1.default.resolve(env_1.env.TEMP_DIRECTORY || './temp');
    app.use('/public', express_1.default.static(publicDir));
    // Home route redirecting to Demo Solution Page
    app.get('/', (req, res) => {
        res.redirect('/solution/demo123');
    });
    // Health Check Endpoint
    app.get('/health', (req, res) => {
        res.json({
            status: 'ok',
            service: 'Telegram AI Math Solver Bot',
            timestamp: new Date().toISOString(),
            env: process.env.NODE_ENV || 'development',
        });
    });
    // Web solution pages
    app.use('/', (0, solution_routes_1.createSolutionRoutes)(solutionService));
    // Production Telegram Webhook endpoint support
    if (env_1.env.WEBHOOK_DOMAIN && env_1.env.WEBHOOK_SECRET) {
        const webhookPath = `/webhook/${env_1.env.WEBHOOK_SECRET}`;
        app.use(bot.webhookCallback(webhookPath));
        logger_1.logger.info(`Registered Telegram Webhook route at: ${webhookPath}`);
    }
    return app;
}
//# sourceMappingURL=server.js.map