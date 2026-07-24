export interface SpellCheckRequest {
    text: string;
    language?: string;
    mode?: string;
    customDictionary?: string[];
}
export interface SpellCheckIssue {
    id: string;
    original: string;
    suggestions: string[];
    replacement: string;
    type: string;
    severity: 'error' | 'warning' | 'suggestion';
    confidence: number;
    start: number;
    end: number;
    explanation: string;
    autoFixable: boolean;
}
export interface SpellCheckResponse {
    success: boolean;
    originalText: string;
    correctedText: string;
    summary: {
        totalIssues: number;
        errors: number;
        warnings: number;
        suggestions: number;
        autoFixable: number;
    };
    issues: SpellCheckIssue[];
}
export declare class SpellCheckService {
    checkSpelling(req: SpellCheckRequest): SpellCheckResponse;
}
