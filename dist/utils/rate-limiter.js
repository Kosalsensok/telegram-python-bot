"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.checkRateLimit = checkRateLimit;
const userRequestTimestamps = new Map();
function checkRateLimit(telegramId, maxRequests = 10, windowSeconds = 60) {
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
//# sourceMappingURL=rate-limiter.js.map