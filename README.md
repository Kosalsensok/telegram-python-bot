<div align="center">

# 🤖 Telegram AI Assistant Bot (24/7 Omnimodal AI)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Framework-Aiogram%20v3-2CA5E0.svg?style=for-the-badge&logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![Gemini](https://img.shields.io/badge/AI_Engine-Gemini_1.5_Flash-8E44AD.svg?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Deployment](https://img.shields.io/badge/Deployment-Render_24%2F7-46E3B7.svg?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)
[![UptimeRobot](https://img.shields.io/badge/Uptime-100%25_Online-brightgreen.svg?style=for-the-badge&logo=uptimerobot&logoColor=white)](https://uptimerobot.com/)

**English:** An advanced, production-grade 24/7 Omnimodal Telegram AI Bot featuring Gemini 1.5 Multimodal Chat, Khmer & Standard LaTeX Math Solver, PNG Solution Card Rendering, AI Image Unblur & Super-Resolution, Piston Code Compiler, Audio Voice Transcription, PDF Document OCR, and Dynamic In-Place Animated Progress Indicators.

**ភាសាខ្មែរ (Khmer):** ជំនួយការ AI Bot ឆ្លាតវៃដំណើរការ 24/7 លើ Telegram ដែលមានសមត្ថភាពខ្ពស់ក្នុងការឆ្លើយសំណួរ, ដោះស្រាយលំហាត់គណិតវិទ្យា/វិទ្យាសាស្ត្រ (បង្កើតជារូបភាព PNG Card ចម្លើយច្បាស់ត្រជាក់ភ្នែក), កែរូបភាពមិនច្បាស់ឲ្យច្បាស់ (AI Unblur HD), បម្លែងសំឡេងជាអក្សរ, វិភាគឯកសារ PDF/រូបថត, ព្រមទាំងរត់ និង ពិនិត្យកូដ C++, Python, Java, JS ភ្លាមៗ! 🚀

---

</div>

## ✨ Key Features (លក្ខណៈពិសេសចម្បងៗ)

| Feature | Description & Capabilities |
| :--- | :--- |
| **🤖 Omnimodal AI Chat** | Powered by Gemini 1.5 Flash/Pro with conversational memory, context retention, and multi-turn chat support. |
| **🖼️ PNG Solution Card Generator** | Automatically renders high-resolution PNG solution cards for math exercise photos with clear Khmer typography and highlighted answer containers. |
| **✨ AI Image Enhancer & Unblur** | `/enhance`, `/unblur`, `/hd` commands using Lanczos 2x super-resolution, Unsharp Masking, and contrast tuning (capped at 1920px for memory efficiency). |
| **🎨 AI Image Generation** | Generate images from text prompts with interactive inline ratio switching (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`) and instant JPG/PNG download options. |
| **💻 Code Execution & Compiler** | Runs C++, Python, Java, JavaScript, and SQL code directly via the Piston Execution API with clean, un-escaped HTML syntax highlighting. |
| **🎙️ Voice Note Transcription** | Converts Telegram voice messages and audio files into accurate Khmer & English text transcripts with instant AI summaries. |
| **📄 PDF & Document OCR** | Extracts and analyzes text from PDF documents, handwritten notes, and scanned images. |
| **🎬 Dynamic Animated Progress** | Real-time in-place progress steps with live icons (`🔄`, `🧠`, `🖼️`, `⚡`) for text, vision, document, and image tasks. |
| **🌐 24/7 Server Keep-Alive** | Built-in HTTP Health Check Server on PORT 10000 with GET/HEAD support, active self-pinging, and UptimeRobot integration. |

---

## 🤖 Operating Modes (របៀបដំណើរការទាំង ៧)

You can easily switch operating modes anytime using the `/mode` command or inline keyboards:

- **🤖 General AI Mode (`general`)**: ជំនួយការ AI ទូទៅសម្រាប់សួរសំណួរ, សរសេរកូដ, វិភាគទិន្នន័យ និង ពិភាក្សា។
- **📐 Standard LaTeX Mode (`standard`)**: បម្លែងរូបមន្តគណិតវិទ្យា, គីមី, រូបវិទ្យា និង តារាងទៅជាកូដ Standard LaTeX។
- **🇰🇭 Khmer Math Mode (`khmer_math`)**: បម្លែងសមីការ និង លំហាត់ដែលមានភាសាខ្មែរ ទៅជា LaTeX ដោយរក្សាពាក្យខ្មែរដដែល។
- **🌐 Translate to ខ្មែរ Mode (`translate_khmer`)**: បកប្រែអត្ថបទ ឯកសារ ឬ រូបភាព ពីគ្រប់ភាសា មកជាភាសាខ្មែរធម្មជាតិ។
- **🎨 TikZ Mode (`tikz`)**: បម្លែងរូបភាព ដ្យាក្រាម សៀគ្វី ឬ ក្រាហ្វ ទៅជាកូដ LaTeX TikZ Diagram។
- **📄 PDF to Text Mode (`pdf_to_text`)**: ទាញយកអត្ថបទសុទ្ធពីឯកសារ PDF ឬ រូបភាពដែលមានអក្សរខ្មែរ។
- **✍️ Handwrite Mode (`handwrite`)**: វិភាគអក្សរដៃ និង សមីការសរសេរដោយដៃ រួចបម្លែងជា LaTeX ព្រមទាំងបង្ហាញដំណោះស្រាយ។

---

## ⚡ Command Cheat Sheet (បញ្ជីពាក្យបញ្ជា)

```bash
/start       - 🚀 ផ្ដើមដំណើរការ Bot និង បង្ហាញម៉ឺនុយមេ (Start & Main Menu)
/help        - ❓ បង្ហាញការណែនាំពីរបៀបប្រើប្រាស់ (Usage Instructions)
/mode        - 🔄 ជ្រើសរើសរបៀបដំណើរការ Bot (Change Operating Mode)
/enhance     - ✨ កែរូបភាពមិនច្បាស់ឲ្យច្បាស់ HD (Unblur & Enhance Photo)
/unblur      - 🖼️ ធ្វើឲ្យរូបភាពច្បាស់ត្រជាក់ភ្នែក (Super-Resolution Unblur)
/hd          - 📸 បម្លែងរូបភាពទៅជា HD Ultra-Clear (High Definition Upgrade)
/gen <prompt>- 🎨 បង្កើតរូបភាពតាមចំណង់ចំណូលចិត្ត (Generate AI Image)
/settings    - ⚙️ កំណត់ការកំណត់ផ្ទាល់ខ្លួន (User Preferences)
/clear       - 🧹 លុបប្រវត្តិសន្ទនា (Clear Conversation Memory)
/info        - ℹ️ មើលព័ត៌មានអំពី Bot (Bot & Profile Information)
/status      - 📊 ពិនិត្យស្ថានភាព Server និង Uptime (Check Health & Memory Status)
```

---

## 🏗️ Tech Stack & Architecture (បច្ចេកវិទ្យាប្រើប្រាស់)

- **Language**: Python 3.10+
- **Bot Framework**: [Aiogram v3](https://docs.aiogram.dev/) (Asynchronous Telegram API)
- **AI Multimodal Engine**: Google Gemini API (`gemini-1.5-flash` & `gemini-1.5-pro`)
- **Image Processing Engine**: Pillow (PIL) for super-resolution, Unsharp Mask, & Solution Card rendering
- **Code Execution API**: Piston API (Multi-language Sandboxed Compiler)
- **Web Server**: Aiohttp HTTP Server (`main.py`) running on `PORT 10000`
- **Hosting & Uptime**: Render Free Web Service + UptimeRobot (24/7 Active Keep-Alive)

---

## 🛠️ Local Installation & Setup (ការដំឡើងលើម៉ាស៊ីនផ្ទាល់)

### 1. Clone Repository
```bash
git clone https://github.com/Kosalsensok/telegram-python-bot.git
cd telegram-python-bot
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
PORT=10000
RENDER_EXTERNAL_URL=https://your-bot-name.onrender.com
```

### 4. Run the Bot
```bash
python main.py
```

---

## 🚀 24/7 Render Deployment Guide (ការដំឡើងលើ Render 24/7)

1. Create a **New Web Service** on [Render](https://render.com/).
2. Connect your GitHub repository `Kosalsensok/telegram-python-bot`.
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `python main.py`
5. Add Environment Variables: `BOT_TOKEN`, `GEMINI_API_KEY`, `PORT` (Default: `10000`).
6. Copy your service health URL (e.g. `https://telegram-python-bot-yt64.onrender.com/health`) and add it as a **5-minute HTTP Monitor** on [UptimeRobot](https://uptimerobot.com/).

---

<div align="center">

### 👨‍💻 Created & Maintained by **Kosal Sensok**

[![GitHub](https://img.shields.io/badge/GitHub-Kosalsensok-181717.svg?style=for-the-badge&logo=github)](https://github.com/Kosalsensok)

*Star ⭐ this repository if you find it helpful!*

</div>