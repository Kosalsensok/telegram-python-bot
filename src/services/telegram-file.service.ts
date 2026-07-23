import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { logger } from '../utils/logger';
import { ensureDirectoryExists } from '../utils/files';

export class TelegramFileService {
  private botToken: string;

  constructor(botToken: string) {
    this.botToken = botToken;
  }

  async downloadTelegramFile(fileId: string, destDir: string): Promise<{ filePath: string; buffer: Buffer; mimeType: string }> {
    ensureDirectoryExists(destDir);

    logger.info(`Fetching file path info from Telegram API for fileId: ${fileId}...`);
    const fileInfoUrl = `https://api.telegram.org/bot${this.botToken}/getFile?file_id=${fileId}`;
    const response = await axios.get(fileInfoUrl);

    if (!response.data.ok || !response.data.result.file_path) {
      throw new Error('Failed to retrieve file path from Telegram API');
    }

    const remoteFilePath = response.data.result.file_path;
    const downloadUrl = `https://api.telegram.org/file/bot${this.botToken}/${remoteFilePath}`;

    const ext = path.extname(remoteFilePath) || '.jpg';
    const localFileName = `photo_${Date.now()}_${Math.random().toString(36).substring(7)}${ext}`;
    const localFilePath = path.join(destDir, localFileName);

    logger.info(`Downloading photo stream from Telegram: ${downloadUrl}...`);
    const fileResponse = await axios.get(downloadUrl, { responseType: 'arraybuffer' });
    const buffer = Buffer.from(fileResponse.data);

    fs.writeFileSync(localFilePath, buffer);

    let mimeType = 'image/jpeg';
    if (ext === '.png') mimeType = 'image/png';
    else if (ext === '.webp') mimeType = 'image/webp';

    return { filePath: localFilePath, buffer, mimeType };
  }
}
