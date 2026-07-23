"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UserService = void 0;
const prisma_1 = require("../database/prisma");
const logger_1 = require("../utils/logger");
const memoryUsers = new Map();
class UserService {
    async getOrCreateUser(telegramId, username, firstName, lastName) {
        const prisma = (0, prisma_1.getPrismaClient)();
        if ((0, prisma_1.isDatabaseConnected)() && prisma) {
            try {
                let user = await prisma.user.findUnique({
                    where: { telegramId: BigInt(telegramId) },
                });
                if (!user) {
                    user = await prisma.user.create({
                        data: {
                            telegramId: BigInt(telegramId),
                            username: username || null,
                            firstName: firstName || null,
                            lastName: lastName || null,
                            language: 'km',
                            selectedMode: 'standard',
                        },
                    });
                }
                else {
                    user = await prisma.user.update({
                        where: { telegramId: BigInt(telegramId) },
                        data: {
                            username: username || user.username,
                            firstName: firstName || user.firstName,
                            lastName: lastName || user.lastName,
                            lastActiveAt: new Date(),
                        },
                    });
                }
                const state = {
                    telegramId,
                    username: user.username || undefined,
                    firstName: user.firstName || undefined,
                    lastName: user.lastName || undefined,
                    language: user.language || 'km',
                    selectedMode: user.selectedMode || 'standard',
                    totalRequests: user.totalRequests,
                };
                memoryUsers.set(telegramId, state);
                return state;
            }
            catch (err) {
                logger_1.logger.warn(`Failed DB operation in UserService for ${telegramId}, falling back to memory.`, err);
            }
        }
        // Memory Fallback
        let state = memoryUsers.get(telegramId);
        if (!state) {
            state = {
                telegramId,
                username,
                firstName,
                lastName,
                language: 'km',
                selectedMode: 'standard',
                totalRequests: 0,
            };
            memoryUsers.set(telegramId, state);
        }
        return state;
    }
    async setUserLanguage(telegramId, language) {
        const state = memoryUsers.get(telegramId);
        if (state)
            state.language = language;
        const prisma = (0, prisma_1.getPrismaClient)();
        if ((0, prisma_1.isDatabaseConnected)() && prisma) {
            try {
                await prisma.user.update({
                    where: { telegramId: BigInt(telegramId) },
                    data: { language },
                });
            }
            catch (err) {
                logger_1.logger.warn(`Failed updating language in DB for ${telegramId}`, err);
            }
        }
    }
    async setUserMode(telegramId, selectedMode) {
        const state = memoryUsers.get(telegramId);
        if (state)
            state.selectedMode = selectedMode;
        const prisma = (0, prisma_1.getPrismaClient)();
        if ((0, prisma_1.isDatabaseConnected)() && prisma) {
            try {
                await prisma.user.update({
                    where: { telegramId: BigInt(telegramId) },
                    data: { selectedMode },
                });
            }
            catch (err) {
                logger_1.logger.warn(`Failed updating mode in DB for ${telegramId}`, err);
            }
        }
    }
    async incrementUserRequests(telegramId) {
        const state = memoryUsers.get(telegramId);
        if (state)
            state.totalRequests += 1;
        const prisma = (0, prisma_1.getPrismaClient)();
        if ((0, prisma_1.isDatabaseConnected)() && prisma) {
            try {
                await prisma.user.update({
                    where: { telegramId: BigInt(telegramId) },
                    data: { totalRequests: { increment: 1 } },
                });
            }
            catch (err) {
                logger_1.logger.warn(`Failed incrementing request count in DB for ${telegramId}`, err);
            }
        }
    }
}
exports.UserService = UserService;
//# sourceMappingURL=user.service.js.map