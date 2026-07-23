"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.retryWithBackoff = retryWithBackoff;
const logger_1 = require("./logger");
async function retryWithBackoff(fn, retries = 3, delayMs = 1000) {
    let attempt = 0;
    while (attempt < retries) {
        try {
            return await fn();
        }
        catch (error) {
            attempt++;
            if (attempt >= retries) {
                throw error;
            }
            const backoff = delayMs * Math.pow(2, attempt - 1);
            logger_1.logger.warn(`Retry attempt ${attempt}/${retries} failed. Waiting ${backoff}ms before retry. Error:`, error);
            await new Promise((res) => setTimeout(res, backoff));
        }
    }
    throw new Error('Retry exhausted');
}
//# sourceMappingURL=retry.js.map