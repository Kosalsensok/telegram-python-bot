import fs from 'fs';
import path from 'path';
import { logger } from './logger';

export function ensureDirectoryExists(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

export function removeFileSafely(filePath: string): void {
  try {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
  } catch (err) {
    logger.warn(`Failed to safely delete temp file ${filePath}:`, err);
  }
}

export function cleanOldTempFiles(dirPath: string, maxAgeMinutes: number = 60): void {
  try {
    if (!fs.existsSync(dirPath)) return;
    const files = fs.readdirSync(dirPath);
    const now = Date.now();
    const maxAgeMs = maxAgeMinutes * 60 * 1000;

    files.forEach((file) => {
      const fullPath = path.join(dirPath, file);
      const stat = fs.statSync(fullPath);
      if (now - stat.mtimeMs > maxAgeMs) {
        removeFileSafely(fullPath);
      }
    });
  } catch (err) {
    logger.warn('Error during temp directory cleanup:', err);
  }
}
