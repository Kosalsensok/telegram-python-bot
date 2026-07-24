import { Router, Request, Response } from 'express';
import { SpellCheckService } from '../../services/spellcheck.service';

export function createSpellCheckRoutes(spellCheckService: SpellCheckService): Router {
  const router = Router();

  router.post('/api/spell-check', (req: Request, res: Response) => {
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
    } catch (err) {
      return res.status(500).json({
        success: false,
        code: 'SPELL_CHECK_FAILED',
        message: 'មិនអាចពិនិត្យអត្ថបទបាននៅពេលនេះទេ។ សូមព្យាយាមម្តងទៀត។',
      });
    }
  });

  return router;
}
