export declare class TelegramFileService {
    private botToken;
    constructor(botToken: string);
    downloadTelegramFile(fileId: string, destDir: string): Promise<{
        filePath: string;
        buffer: Buffer;
        mimeType: string;
    }>;
}
