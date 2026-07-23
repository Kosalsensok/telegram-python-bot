"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.StorageService = void 0;
const path_1 = __importDefault(require("path"));
const env_1 = require("../config/env");
const files_1 = require("../utils/files");
class StorageService {
    tempDir;
    constructor() {
        this.tempDir = path_1.default.resolve(env_1.env.TEMP_DIRECTORY || './temp');
        (0, files_1.ensureDirectoryExists)(this.tempDir);
    }
    getTempPath(filename) {
        return path_1.default.join(this.tempDir, filename);
    }
    deleteFile(filePath) {
        (0, files_1.removeFileSafely)(filePath);
    }
}
exports.StorageService = StorageService;
//# sourceMappingURL=storage.service.js.map