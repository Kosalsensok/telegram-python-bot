"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TelegramFileService = void 0;
const axios_1 = __importDefault(require("axios"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const logger_1 = require("../utils/logger");
const files_1 = require("../utils/files");
class TelegramFileService {
    botToken;
    constructor(botToken) {
        this.botToken = botToken;
    }
    async downloadTelegramFile(fileId, destDir) {
        (0, files_1.ensureDirectoryExists)(destDir);
        logger_1.logger.info(`Fetching file path info from Telegram API for fileId: ${fileId}...`);
        const fileInfoUrl = `https://api.telegram.org/bot${this.botToken}/getFile?file_id=${fileId}`;
        const response = await axios_1.default.get(fileInfoUrl);
        if (!response.data.ok || !response.data.result.file_path) {
            throw new Error('Failed to retrieve file path from Telegram API');
        }
        const remoteFilePath = response.data.result.file_path;
        const downloadUrl = `https://api.telegram.org/file/bot${this.botToken}/${remoteFilePath}`;
        const ext = path_1.default.extname(remoteFilePath) || '.jpg';
        const localFileName = `photo_${Date.now()}_${Math.random().toString(36).substring(7)}${ext}`;
        const localFilePath = path_1.default.join(destDir, localFileName);
        logger_1.logger.info(`Downloading photo stream from Telegram: ${downloadUrl}...`);
        const fileResponse = await axios_1.default.get(downloadUrl, { responseType: 'arraybuffer' });
        const buffer = Buffer.from(fileResponse.data);
        fs_1.default.writeFileSync(localFilePath, buffer);
        let mimeType = 'image/jpeg';
        if (ext === '.png')
            mimeType = 'image/png';
        else if (ext === '.webp')
            mimeType = 'image/webp';
        return { filePath: localFilePath, buffer, mimeType };
    }
}
exports.TelegramFileService = TelegramFileService;
//# sourceMappingURL=telegram-file.service.js.map