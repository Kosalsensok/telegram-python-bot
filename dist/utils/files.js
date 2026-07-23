"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ensureDirectoryExists = ensureDirectoryExists;
exports.removeFileSafely = removeFileSafely;
exports.cleanOldTempFiles = cleanOldTempFiles;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const logger_1 = require("./logger");
function ensureDirectoryExists(dirPath) {
    if (!fs_1.default.existsSync(dirPath)) {
        fs_1.default.mkdirSync(dirPath, { recursive: true });
    }
}
function removeFileSafely(filePath) {
    try {
        if (fs_1.default.existsSync(filePath)) {
            fs_1.default.unlinkSync(filePath);
        }
    }
    catch (err) {
        logger_1.logger.warn(`Failed to safely delete temp file ${filePath}:`, err);
    }
}
function cleanOldTempFiles(dirPath, maxAgeMinutes = 60) {
    try {
        if (!fs_1.default.existsSync(dirPath))
            return;
        const files = fs_1.default.readdirSync(dirPath);
        const now = Date.now();
        const maxAgeMs = maxAgeMinutes * 60 * 1000;
        files.forEach((file) => {
            const fullPath = path_1.default.join(dirPath, file);
            const stat = fs_1.default.statSync(fullPath);
            if (now - stat.mtimeMs > maxAgeMs) {
                removeFileSafely(fullPath);
            }
        });
    }
    catch (err) {
        logger_1.logger.warn('Error during temp directory cleanup:', err);
    }
}
//# sourceMappingURL=files.js.map