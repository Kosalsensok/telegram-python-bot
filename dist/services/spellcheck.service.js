"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SpellCheckService = void 0;
const KHMER_RULES = {
    'សំរាប់': { suggestions: ['សម្រាប់'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រាប់»។', autoFixable: true, severity: 'error', confidence: 0.96 },
    'សំរេច': { suggestions: ['សម្រេច'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រេច»។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'សំរួល': { suggestions: ['សម្រួល'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រួល»។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'អោយ': { suggestions: ['ឱ្យ'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «ឱ្យ»។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'រឺ': { suggestions: ['ឬ'], explanation: 'សញ្ញាឈ្នាប់ «ឬ» ត្រូវសរសេរដោយប្រើតួអក្សរ ឬ មិនមែន រឺ ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.96 },
    'កំនត់': { suggestions: ['កំណត់'], explanation: 'ពាក្យ «កំណត់» ប្រើប្រកប «ំណ» មិនមែន «ំន» ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'បំនង': { suggestions: ['បំណង'], explanation: 'ពាក្យ «បំណង» ប្រើប្រកប «ំណ» មិនមែន «ំន» ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'តំលៃ': { suggestions: ['តម្លៃ'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «តម្លៃ»។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'តំឡើង': { suggestions: ['ដំឡើង', 'តម្លើង'], explanation: 'ពាក្យនេះជាទូទៅត្រូវសរសេរជា «ដំឡើង»។', autoFixable: true, severity: 'warning', confidence: 0.90 },
    'ចំនុច': { suggestions: ['ចំណុច'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «ចំណុច»។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'ចំនែក': { suggestions: ['ចំណែក'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «ចំណែក»។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'ចំនាយ': { suggestions: ['ចំណាយ'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «ចំណាយ»។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'ចំនូល': { suggestions: ['ចំណូល'], explanation: 'ពាក្យនេះត្រូវសរសេរជា «ចំណូល»។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'ប្រពន្ធ័': { suggestions: ['ប្រព័ន្ធ'], explanation: 'ពាក្យ «ប្រព័ន្ធ» ប្រើទណ្ឌឃាតលើ ័ មិនមែន ័ ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.96 },
    'ពិេសស': { suggestions: ['ពិសេស'], explanation: 'ស្រៈ «េ» ត្រូវស្ថិតនៅមុនព្យញ្ជនៈស។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'សម្ភារៈ': { suggestions: ['សម្ភារ'], explanation: 'ពាក្យ «សម្ភារ» មិនត្រូវមាន ៈ នៅខាងចុងឡើយ។', autoFixable: true, severity: 'warning', confidence: 0.92 },
    'អុីនធឺណិត': { suggestions: ['អ៊ីនធឺណិត'], explanation: 'ពាក្យ «អ៊ីនធឺណិត» ត្រូវប្រើស្រៈ អ៊ី មិនមែន អុី ឡើយ។', autoFixable: true, severity: 'error', confidence: 0.95 },
    'សន្តិភព': { suggestions: ['សន្តិភាព'], explanation: 'ពាក្យ «សន្តិភាព» ត្រូវមានស្រៈ ា។', autoFixable: true, severity: 'error', confidence: 0.94 },
};
const EXCLUSION_PATTERNS = [
    /https?:\/\/[^\s]+/gi,
    /www\.[^\s]+/gi,
    /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/gi,
    /\+?\d{8,15}/g,
    /@[a-zA-Z0-9_]{3,}/g,
    /#[a-zA-Z0-9_\u1780-\u17FF]+/g,
    /\/[a-zA-Z0-9_]+/g,
    /```[\s\S]*?```/g,
    /`[^`]+`/g,
    /\{[\s\S]*?\}/g,
    /<[^>]+>/g,
];
class SpellCheckService {
    checkSpelling(req) {
        const text = (req.text || '').substring(0, 5000);
        const customSet = new Set((req.customDictionary || []).map(w => w.trim()));
        const protectedRanges = [];
        for (const pat of EXCLUSION_PATTERNS) {
            let match;
            while ((match = pat.exec(text)) !== null) {
                protectedRanges.push([match.index, match.index + match[0].length]);
            }
        }
        const isProtected = (start, end) => {
            for (const [pStart, pEnd] of protectedRanges) {
                if (Math.max(start, pStart) < Math.min(end, pEnd))
                    return true;
            }
            return false;
        };
        const issues = [];
        let issueCount = 1;
        for (const [wordKey, rule] of Object.entries(KHMER_RULES)) {
            if (customSet.has(wordKey))
                continue;
            let pos = text.indexOf(wordKey);
            while (pos !== -1) {
                const endPos = pos + wordKey.length;
                if (!isProtected(pos, endPos)) {
                    issues.push({
                        id: `issue_${issueCount++}`,
                        original: wordKey,
                        suggestions: rule.suggestions,
                        replacement: rule.suggestions[0],
                        type: 'spelling',
                        severity: rule.severity,
                        confidence: rule.confidence,
                        start: pos,
                        end: endPos,
                        explanation: rule.explanation,
                        autoFixable: rule.autoFixable && rule.confidence >= 0.90,
                    });
                }
                pos = text.indexOf(wordKey, pos + 1);
            }
        }
        // Check double space
        const doubleSpaceRegex = / {2,}/g;
        let dsMatch;
        while ((dsMatch = doubleSpaceRegex.exec(text)) !== null) {
            const pos = dsMatch.index;
            const endPos = pos + dsMatch[0].length;
            if (!isProtected(pos, endPos)) {
                issues.push({
                    id: `issue_${issueCount++}`,
                    original: dsMatch[0],
                    suggestions: [' '],
                    replacement: ' ',
                    type: 'spacing',
                    severity: 'warning',
                    confidence: 0.98,
                    start: pos,
                    end: endPos,
                    explanation: 'មានចន្លោះច្រើនជាប់គ្នា។ គួរប្រើចន្លោះតែមួយ។',
                    autoFixable: true,
                });
            }
        }
        issues.sort((a, b) => a.start - b.start);
        let correctedText = text;
        for (const issue of [...issues].sort((a, b) => b.start - a.start)) {
            if (issue.autoFixable && issue.replacement) {
                correctedText = correctedText.substring(0, issue.start) + issue.replacement + correctedText.substring(issue.end);
            }
        }
        return {
            success: true,
            originalText: text,
            correctedText,
            summary: {
                totalIssues: issues.length,
                errors: issues.filter(i => i.severity === 'error').length,
                warnings: issues.filter(i => i.severity === 'warning').length,
                suggestions: issues.filter(i => i.severity === 'suggestion').length,
                autoFixable: issues.filter(i => i.autoFixable).length,
            },
            issues,
        };
    }
}
exports.SpellCheckService = SpellCheckService;
//# sourceMappingURL=spellcheck.service.js.map