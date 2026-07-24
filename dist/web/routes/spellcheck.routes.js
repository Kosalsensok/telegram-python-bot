"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createSpellCheckRoutes = createSpellCheckRoutes;
const express_1 = require("express");
function createSpellCheckRoutes(spellCheckService) {
    const router = (0, express_1.Router)();
    router.post('/api/spell-check', (req, res) => {
        const text = req.body?.text;
        if (!text || typeof text !== 'string' || !text.trim()) {
            return res.status(400).json({
                success: false,
                code: 'EMPTY_TEXT',
                message: 'សូមបញ្ចូលអត្ថបទជាមុនសិន។',
            });
        }
        if (text.length > 5000) {
            return res.status(400).json({
                success: false,
                code: 'TEXT_TOO_LONG',
                message: 'អត្ថបទមានប្រវែងលើស 5,000 តួអក្សរ។',
            });
        }
        try {
            const result = spellCheckService.checkSpelling({
                text,
                language: req.body.language || 'km',
                mode: req.body.mode || 'standard',
                customDictionary: req.body.customDictionary || [],
            });
            return res.json(result);
        }
        catch (err) {
            return res.status(500).json({
                success: false,
                code: 'SPELL_CHECK_FAILED',
                message: 'មិនអាចពិនិត្យអត្ថបទបាននៅពេលនេះទេ។ សូមព្យាយាមម្តងទៀត។',
            });
        }
    });
    return router;
}
//# sourceMappingURL=spellcheck.routes.js.map