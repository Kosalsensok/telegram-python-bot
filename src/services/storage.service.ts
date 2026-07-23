import path from 'path';
import { env } from '../config/env';
import { ensureDirectoryExists, removeFileSafely } from '../utils/files';

export class StorageService {
  private tempDir: string;

  constructor() {
    this.tempDir = path.resolve(env.TEMP_DIRECTORY || './temp');
    ensureDirectoryExists(this.tempDir);
  }

  getTempPath(filename: string): string {
    return path.join(this.tempDir, filename);
  }

  deleteFile(filePath: string): void {
    removeFileSafely(filePath);
  }
}
