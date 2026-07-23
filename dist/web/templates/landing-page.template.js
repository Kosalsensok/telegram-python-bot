"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.renderLandingPageHtml = renderLandingPageHtml;
function renderLandingPageHtml(appUrl, botUsername) {
    const telegramBotUrl = `https://t.me/${botUsername || 'mysmart_v2_2026_bot'}`;
    return `<!DOCTYPE html>
<html lang="km">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart AI Math Solver | វេទិកាដោះស្រាយលំហាត់គណិតវិទ្យា AI ឆ្លាតវៃ</title>

  <!-- Favicon Icon -->
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232563EB' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='16' height='20' x='4' y='2' rx='2'/%3E%3Cline x1='8' x2='16' y1='6' y2='6'/%3E%3Cline x1='16' x2='16' y1='14' y2='18'/%3E%3Cpath d='M16 10h.01'/%3E%3Cpath d='M12 10h.01'/%3E%3Cpath d='M8 10h.01'/%3E%3Cpath d='M12 14h.01'/%3E%3Cpath d='M8 14h.01'/%3E%3Cpath d='M12 18h.01'/%3E%3Cpath d='M8 18h.01'/%3E%3C/svg%3E">
  
  <meta name="title" content="Smart AI Math Solver | Official Platform">
  <meta name="description" content="Official Smart AI Math Solver platform for students, teachers, and universities. Instant step-by-step solutions powered by Gemini AI.">

  <!-- KaTeX CSS -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+Khmer:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Lucide Icons & KaTeX JS -->
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>

  <style>
    :root {
      --primary-dark: #123B8F;
      --primary-blue: #2563EB;
      --primary-bright: #3B82F6;
      --bg-main: #F6F9FD;
      --bg-card: #FFFFFF;
      --bg-soft-blue: #EFF6FF;
      --text-main: #0F172A;
      --text-secondary: #475569;
      --text-muted: #64748B;
      --border-color: #E2E8F0;
      --radius-card: 16px;
      --shadow-card: 0 10px 30px -4px rgba(18, 59, 143, 0.08);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Noto Sans Khmer', 'Inter', -apple-system, sans-serif;
      background: var(--bg-main);
      color: var(--text-main);
      line-height: 1.6;
    }

    .navbar {
      background: rgba(255,255,255,0.95);
      backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .nav-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 16px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
    }
    .brand-icon {
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, var(--primary-dark), var(--primary-blue));
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }
    .brand-text h1 { font-size: 18px; color: var(--primary-dark); font-weight: 700; }
    .brand-text p { font-size: 12px; color: var(--text-muted); }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .btn-primary { background: var(--primary-blue); color: white; border: none; }
    .btn-primary:hover { background: var(--primary-dark); }
    .btn-outline { background: white; border: 1px solid var(--border-color); color: var(--text-secondary); }
    .btn-outline:hover { background: var(--bg-soft-blue); color: var(--primary-blue); border-color: var(--primary-bright); }

    .hero {
      padding: 80px 24px 60px;
      max-width: 1200px;
      margin: 0 auto;
      text-align: center;
    }
    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--bg-soft-blue);
      color: var(--primary-blue);
      padding: 6px 16px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 24px;
      border: 1px solid rgba(37, 99, 235, 0.2);
    }
    .hero h1 {
      font-size: 42px;
      font-weight: 800;
      color: var(--primary-dark);
      margin-bottom: 20px;
      line-height: 1.2;
    }
    .hero p {
      font-size: 18px;
      color: var(--text-secondary);
      max-width: 760px;
      margin: 0 auto 36px;
    }
    .hero-actions {
      display: flex;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
    }

    .section {
      max-width: 1200px;
      margin: 0 auto;
      padding: 60px 24px;
    }
    .section-title {
      text-align: center;
      font-size: 28px;
      font-weight: 700;
      color: var(--primary-dark);
      margin-bottom: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 24px;
    }
    .feature-card {
      background: white;
      border-radius: var(--radius-card);
      padding: 28px;
      border: 1px solid var(--border-color);
      box-shadow: var(--shadow-card);
      text-align: left;
    }
    .feature-icon {
      width: 48px;
      height: 48px;
      background: var(--bg-soft-blue);
      color: var(--primary-blue);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;
    }
    .feature-card h3 { font-size: 18px; font-weight: 700; color: var(--primary-dark); margin-bottom: 10px; }
    .feature-card p { font-size: 14px; color: var(--text-secondary); }

    .subjects-grid {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 14px;
    }
    .subject-pill {
      background: white;
      border: 1px solid var(--border-color);
      padding: 12px 24px;
      border-radius: 12px;
      font-size: 15px;
      font-weight: 600;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }

    .footer {
      background: white;
      border-top: 1px solid var(--border-color);
      padding: 40px 24px;
      margin-top: 60px;
    }
    .footer-content {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
      font-size: 14px;
      color: var(--text-muted);
    }

    @media (max-width: 768px) {
      .hero h1 { font-size: 30px; }
      .hero p { font-size: 15px; }
    }
  </style>
</head>
<body>

  <header class="navbar">
    <div class="nav-container">
      <a href="/" class="brand">
        <div class="brand-icon"><i data-lucide="calculator"></i></div>
        <div class="brand-text">
          <h1>Smart AI Math Solver</h1>
          <p>Official Solution Platform</p>
        </div>
      </a>
      <div>
        <a href="${telegramBotUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
          <i data-lucide="send"></i> Open Telegram Bot
        </a>
      </div>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="hero-badge"><i data-lucide="sparkles"></i> Powered by Gemini 2.0 Flash AI</div>
      <h1><i data-lucide="award" style="color: var(--primary-blue);"></i> ប្រព័ន្ធដោះស្រាយលំហាត់គណិតវិទ្យា AI ឆ្លាតវៃ<br><span style="color: var(--primary-blue);">Smart AI Math Solver Platform</span></h1>
      <p>
        វេទិកាផ្លូវការសម្រាប់សិស្ស គ្រូបង្រៀន និងសាកលវិទ្យាល័យ ក្នុងការដោះស្រាយលំហាត់គណិតវិទ្យា រូបវិទ្យា និងគីមីវិទ្យា ដោយបង្ហាញដំណោះស្រាយលម្អិតជាជំហានៗ (Step-by-step) ប្រកបដោយទំនុកចិត្ត និងភាពច្បាស់លាស់។
      </p>
      <div class="hero-actions">
        <a href="/solution/demo123" class="btn btn-primary" style="padding: 14px 28px; font-size: 16px;">
          <i data-lucide="eye"></i> មើលឧទាហរណ៍ដំណោះស្រាយ (View Demo Solution)
        </a>
        <a href="${telegramBotUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-outline" style="padding: 14px 28px; font-size: 16px;">
          <i data-lucide="bot"></i> ចាប់ផ្តើមប្រើប្រាស់លើ Telegram
        </a>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title"><i data-lucide="sparkles" style="color: var(--primary-blue);"></i> លក្ខណៈពិសេសចម្បង (Key Features)</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon"><i data-lucide="layers"></i></div>
          <h3>ដំណោះស្រាយជាជំហានៗ</h3>
          <p>បង្ហាញពីវិធីសាស្ត្រដោះស្រាយលម្អិត ព្រមទាំងការពន្យល់ និងរូបមន្តត្រឹមត្រូវដើម្បីងាយស្រួលយល់។</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon"><i data-lucide="binary"></i></div>
          <h3>KaTeX High-Precision Math</h3>
          <p>រៀបចំរូបមន្តគណិតវិទ្យា ប្រភាគ អាំងតេក្រាល និងម៉ាទ្រីស យ៉ាងច្បាស់លាស់ ស្អាត និងផ្លូវការ។</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon"><i data-lucide="languages"></i></div>
          <h3>គាំទ្រ ភាសាខ្មែរ & អង់គ្លេស</h3>
          <p>អាចផ្លាស់ប្តូរភាសា (Khmer / English) បានភ្លាមៗតាមតម្រូវការប្រើប្រាស់។</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon"><i data-lucide="printer"></i></div>
          <h3>ទាញយកជា PDF & Print</h3>
          <p>អាច Export និង Save ដំណោះស្រាយជាទម្រង់ PDF សម្រាប់ព្រីនចេញ ឬរក្សាទុកសិក្សា។</p>
        </div>
      </div>
    </section>

    <section class="section" style="background: white; border-radius: 24px; border: 1px solid var(--border-color); box-shadow: var(--shadow-card);">
      <h2 class="section-title" style="margin-bottom: 24px;"><i data-lucide="book-open" style="color: var(--primary-blue);"></i> មុខវិជ្ជាដែលគាំទ្រ (Supported Subjects)</h2>
      <div class="subjects-grid">
        <div class="subject-pill"><i data-lucide="plus-slash-minus" style="color: var(--primary-blue);"></i> Mathematics (គណិតវិទ្យា)</div>
        <div class="subject-pill"><i data-lucide="atom" style="color: var(--primary-blue);"></i> Physics (រូបវិទ្យា)</div>
        <div class="subject-pill"><i data-lucide="flask-conical" style="color: var(--primary-blue);"></i> Chemistry (គីមីវិទ្យា)</div>
        <div class="subject-pill"><i data-lucide="variable" style="color: var(--primary-blue);"></i> Algebra & Geometry</div>
        <div class="subject-pill"><i data-lucide="trending-up" style="color: var(--primary-blue);"></i> Calculus & Statistics</div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="footer-content">
      <div style="display:flex; align-items:center; gap:8px;">
        <i data-lucide="calculator" style="color: var(--primary-blue);"></i> <strong style="color: var(--primary-dark);">Smart AI Math Solver Platform</strong> — © 2026. All rights reserved.
      </div>
      <div>
        <a href="${telegramBotUrl}" target="_blank" rel="noopener noreferrer" style="color: var(--primary-blue); text-decoration: none; font-weight: 600;">
          <i data-lucide="send" style="display: inline; width: 14px;"></i> Telegram Bot
        </a>
      </div>
    </div>
  </footer>

  <script>
    lucide.createIcons();
  </script>
</body>
</html>`;
}
//# sourceMappingURL=landing-page.template.js.map