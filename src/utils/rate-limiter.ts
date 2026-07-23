const userRequestTimestamps = new Map<number, number[]>();

export function checkRateLimit(telegramId: number, maxRequests: number = 10, windowSeconds: number = 60): boolean {
  const now = Date.now();
  const windowMs = windowSeconds * 1000;
  let timestamps = userRequestTimestamps.get(telegramId) || [];

  // Filter timestamps within current window
  timestamps = timestamps.filter((t) => now - t < windowMs);

  if (timestamps.length >= maxRequests) {
    return false; // Exceeded limit
  }

  timestamps.push(now);
  userRequestTimestamps.set(telegramId, timestamps);
  return true;
}
