export const EnglishMessages = {
  welcome: (name: string) => `<b>🤖 Smart AI Math Solver Bot</b>\n\n<blockquote>Hello ${name}! 👋\nSend a photo of any math, chemistry, physics problem or equation to get an instant step-by-step LaTeX solution!</blockquote>\n\n<b>✨ Key Features:</b>\n• 🖼 Analyze and solve math from photos\n• 📐 Render formulas with standard LaTeX\n• 🎨 Generate high-res solution cards & PDFs\n• 🌐 Khmer & English language support`,
  
  help: `📖 <b>Usage Guide:</b>\n\n1. <b>Send a photo:</b> Click Attach Photo and send a clear image of your problem/equation.\n2. <b>Select Mode (/mode):</b> Choose Standard Math, Khmer Math, Detailed Solution, Quick Answer, Chemistry, Physics, or Table mode.\n3. <b>Select Language (/language):</b> Switch responses between Khmer and English.`,

  step1: '📥 Photo received...',
  step2: '🔍 Extracting questions and equations...',
  step3: '🧠 Calculating step-by-step solution...',
  step4: '🎨 Rendering solution image...',

  captionSuccess: (botUsername: string) => `🎓 <b>Solution Ready!</b>\n\n✅ Analyzed problem\n🧠 Solved step-by-step\n📐 Rendered with LaTeX\n\n⚡ ${botUsername}`,

  blurryImage: '⚠️ The image is blurry. Please send a clearer picture of the problem.',
  noProblemDetected: '🔍 Could not detect any math questions in this photo. Please send a clear image.',
  aiError: '❌ Failed to analyze problem. Please try again.',
  renderingError: '🎨 Solution image rendering error. System retrying...',
  rateLimit: '⏳ Rate limit exceeded. Please wait a moment before sending another request.',
};
