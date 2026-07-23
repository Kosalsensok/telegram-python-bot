import { PrismaClient } from '@prisma/client';
export declare function getPrismaClient(): PrismaClient | null;
export declare function testDbConnection(): Promise<boolean>;
export declare function isDatabaseConnected(): boolean;
