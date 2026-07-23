"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getPrismaClient = getPrismaClient;
exports.testDbConnection = testDbConnection;
exports.isDatabaseConnected = isDatabaseConnected;
const client_1 = require("@prisma/client");
const logger_1 = require("../utils/logger");
let prisma = null;
let isDbConnected = false;
function getPrismaClient() {
    if (!prisma) {
        try {
            prisma = new client_1.PrismaClient({
                log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
            });
        }
        catch (err) {
            logger_1.logger.warn('Failed to construct PrismaClient instance. Using fallback state.', err);
            return null;
        }
    }
    return prisma;
}
async function testDbConnection() {
    const client = getPrismaClient();
    if (!client) {
        isDbConnected = false;
        return false;
    }
    try {
        await client.$queryRaw `SELECT 1`;
        isDbConnected = true;
        logger_1.logger.info('✅ Connected to MySQL database via Prisma ORM.');
        return true;
    }
    catch (error) {
        isDbConnected = false;
        logger_1.logger.warn('⚠️ MySQL database connection unavailable. Operating in graceful fallback mode.', error);
        return false;
    }
}
function isDatabaseConnected() {
    return isDbConnected;
}
//# sourceMappingURL=prisma.js.map