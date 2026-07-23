import { PrismaClient } from '@prisma/client';
import { logger } from '../utils/logger';

let prisma: PrismaClient | null = null;
let isDbConnected = false;

export function getPrismaClient(): PrismaClient | null {
  if (!prisma) {
    try {
      prisma = new PrismaClient({
        log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
      });
    } catch (err) {
      logger.warn('Failed to construct PrismaClient instance. Using fallback state.', err);
      return null;
    }
  }
  return prisma;
}

export async function testDbConnection(): Promise<boolean> {
  const client = getPrismaClient();
  if (!client) {
    isDbConnected = false;
    return false;
  }
  try {
    await client.$queryRaw`SELECT 1`;
    isDbConnected = true;
    logger.info('✅ Connected to MySQL database via Prisma ORM.');
    return true;
  } catch (error) {
    isDbConnected = false;
    logger.warn('⚠️ MySQL database connection unavailable. Operating in graceful fallback mode.', error);
    return false;
  }
}

export function isDatabaseConnected(): boolean {
  return isDbConnected;
}
