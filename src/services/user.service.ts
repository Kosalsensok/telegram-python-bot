import { getPrismaClient, isDatabaseConnected } from '../database/prisma';
import { logger } from '../utils/logger';

export interface UserState {
  telegramId: number;
  username?: string;
  firstName?: string;
  lastName?: string;
  language: 'km' | 'en';
  selectedMode: string;
  totalRequests: number;
}

const memoryUsers = new Map<number, UserState>();

export class UserService {
  async getOrCreateUser(
    telegramId: number,
    username?: string,
    firstName?: string,
    lastName?: string
  ): Promise<UserState> {
    const prisma = getPrismaClient();

    if (isDatabaseConnected() && prisma) {
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
        } else {
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

        const state: UserState = {
          telegramId,
          username: user.username || undefined,
          firstName: user.firstName || undefined,
          lastName: user.lastName || undefined,
          language: (user.language as 'km' | 'en') || 'km',
          selectedMode: user.selectedMode || 'standard',
          totalRequests: user.totalRequests,
        };

        memoryUsers.set(telegramId, state);
        return state;
      } catch (err) {
        logger.warn(`Failed DB operation in UserService for ${telegramId}, falling back to memory.`, err);
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

  async setUserLanguage(telegramId: number, language: 'km' | 'en'): Promise<void> {
    const state = memoryUsers.get(telegramId);
    if (state) state.language = language;

    const prisma = getPrismaClient();
    if (isDatabaseConnected() && prisma) {
      try {
        await prisma.user.update({
          where: { telegramId: BigInt(telegramId) },
          data: { language },
        });
      } catch (err) {
        logger.warn(`Failed updating language in DB for ${telegramId}`, err);
      }
    }
  }

  async setUserMode(telegramId: number, selectedMode: string): Promise<void> {
    const state = memoryUsers.get(telegramId);
    if (state) state.selectedMode = selectedMode;

    const prisma = getPrismaClient();
    if (isDatabaseConnected() && prisma) {
      try {
        await prisma.user.update({
          where: { telegramId: BigInt(telegramId) },
          data: { selectedMode },
        });
      } catch (err) {
        logger.warn(`Failed updating mode in DB for ${telegramId}`, err);
      }
    }
  }

  async incrementUserRequests(telegramId: number): Promise<void> {
    const state = memoryUsers.get(telegramId);
    if (state) state.totalRequests += 1;

    const prisma = getPrismaClient();
    if (isDatabaseConnected() && prisma) {
      try {
        await prisma.user.update({
          where: { telegramId: BigInt(telegramId) },
          data: { totalRequests: { increment: 1 } },
        });
      } catch (err) {
        logger.warn(`Failed incrementing request count in DB for ${telegramId}`, err);
      }
    }
  }
}
