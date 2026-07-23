export declare const env: {
    BOT_TOKEN: string;
    BOT_USERNAME: string;
    AI_PROVIDER: "openai" | "gemini";
    OPENAI_MODEL: string;
    GEMINI_API_KEY: string;
    GEMINI_MODEL: string;
    DATABASE_URL: string;
    APP_URL: string;
    PORT: number;
    MAX_IMAGE_SIZE_MB: number;
    TEMP_DIRECTORY: string;
    STORAGE_DRIVER: "local" | "s3";
    STORAGE_PUBLIC_URL: string;
    LOG_LEVEL: "error" | "warn" | "info" | "debug";
    OPENAI_API_KEY?: string | undefined;
    WEBHOOK_DOMAIN?: string | undefined;
    WEBHOOK_SECRET?: string | undefined;
};
