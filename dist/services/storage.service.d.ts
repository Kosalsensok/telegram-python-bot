export declare class StorageService {
    private tempDir;
    constructor();
    getTempPath(filename: string): string;
    deleteFile(filePath: string): void;
}
