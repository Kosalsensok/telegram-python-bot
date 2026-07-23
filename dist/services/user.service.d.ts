export interface UserState {
    telegramId: number;
    username?: string;
    firstName?: string;
    lastName?: string;
    language: 'km' | 'en';
    selectedMode: string;
    totalRequests: number;
}
export declare class UserService {
    getOrCreateUser(telegramId: number, username?: string, firstName?: string, lastName?: string): Promise<UserState>;
    setUserLanguage(telegramId: number, language: 'km' | 'en'): Promise<void>;
    setUserMode(telegramId: number, selectedMode: string): Promise<void>;
    incrementUserRequests(telegramId: number): Promise<void>;
}
