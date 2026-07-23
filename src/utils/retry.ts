import { logger } from './logger';

export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  retries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let attempt = 0;
  while (attempt < retries) {
    try {
      return await fn();
    } catch (error) {
      attempt++;
      if (attempt >= retries) {
        throw error;
      }
      const backoff = delayMs * Math.pow(2, attempt - 1);
      logger.warn(`Retry attempt ${attempt}/${retries} failed. Waiting ${backoff}ms before retry. Error:`, error);
      await new Promise((res) => setTimeout(res, backoff));
    }
  }
  throw new Error('Retry exhausted');
}
