"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.renderNotFoundHtml = renderNotFoundHtml;
function renderNotFoundHtml(publicId, botUsername) {
    const telegramBotUrl = `https://t.me/${botUsername || 'mysmart_v2_2026_bot'}`;
    return `<!DOCTYPE html>
<html lang="km">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>404 - Solution Not Found | Smart AI Math Solver</title>
  
  <!-- Fonts & Lucide -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+Khmer:wght@400;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest"></script>

  <style>
    body {
      font-family: 'Noto Sans Khmer', 'Inter', sans-serif;
      background: #F6F9FD;
      color: #0F172A;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      padding: 24px;
    }
    .card {
      background: white;
      border-radius: 20px;
      padding: 48px 32px;
      max-width: 480px;
      width: 100%;
      text-align: center;
      border: 1px solid #E2E8F0;
      box-shadow: 0 10px 30px rgba(18, 59, 143, 0.08);
    }
    .icon-box {
      width: 64px;
      height: 64px;
      background: #EFF6FF;
      color: #2563EB;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 20px;
    }
    h1 { font-size: 24px; font-weight: 700; color: #123B8F; margin-bottom: 12px; }
    p { font-size: 14px; color: #64748B; margin-bottom: 28px; line-height: 1.6; }
    .actions { display: flex; flex-direction: column; gap: 12px; }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .btn-primary { background: #2563EB; color: white; border: none; }
    .btn-primary:hover { background: #123B8F; }
    .btn-outline { background: white; border: 1px solid #E2E8F0; color: #475569; }
    .btn-outline:hover { background: #EFF6FF; color: #2563EB; }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon-box"><i data-lucide="file-question" style="width:32px; height:32px;"></i></div>
    <h1>404 - រកមិនឃើញដំណោះស្រាយ</h1>
    <p>
      រកមិនឃើញដំណោះស្រាយសម្រាប់លេខកូដ #${publicId} ឡើយ។ វាអាចត្រូវបានលុប ឬលេខកូដនេះមិនទាន់ត្រឹមត្រូវ។
    </p>
    <div class="actions">
      <a href="/solution/demo123" class="btn btn-primary">
        <i data-lucide="eye"></i> មើលឧទាហរណ៍ដំណោះស្រាយ (View Demo)
      </a>
      <a href="/" class="btn btn-outline">
        <i data-lucide="home"></i> ត្រឡប់ទៅទំព័រដើម (Home)
      </a>
      <a href="${telegramBotUrl}" target="_blank" class="btn btn-outline">
        <i data-lucide="send"></i> សួរ AI លើ Telegram Bot
      </a>
    </div>
  </div>
  <script>lucide.createIcons();</script>
</body>
</html>`;
}
//# sourceMappingURL=not-found.template.js.map