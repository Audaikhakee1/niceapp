import os
import uvicorn
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from fastapi import FastAPI

app = FastAPI()

# --- مفاتيح القائد المعتمدة ---
TELEGRAM_TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs"
ADMIN_ID = 7955469863
# المفتاح الذي أرسلته (تم وضعه هنا مباشرة للسرعة، لكن يفضل نقله لـ Variables لاحقاً)
KIMI_API_KEY = "sk-zo0vcFZSzR6lW3fe4tua6TDgkIRB2ZNM0gkY7scikzV4CicL"

async def ask_kimi(prompt):
    """محرك Kimi الأساسي - للتحليل والدردشة العميقة"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {KIMI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "system", "content": "أنت 'الوحش الرقمي'، مساعد ذكي وقوي يعمل تحت إمرة القائد 7955469863. ردودك ذكية، مباشرة، وشجاعة."},
            {"role": "user", "content": prompt}
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"⚠️ تنبيه: المحرك يواجه ضغطاً (كود {response.status_code})"
        except Exception as e:
            return f"⚙️ عطل طارئ: {str(e)[:50]}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # حماية القائد
    if update.effective_user.id != ADMIN_ID:
        return 

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # تنفيذ الطلب عبر عقل Kimi
    answer = await ask_kimi(update.message.text)
    await update.message.reply_text(answer)

# --- أوامر السيطرة ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("⚡ الوحش استيقظ. العقل (Kimi) متصل، النفق الرقمي مفتوح، وأنا تحت إمرتك أيها القائد.")

@app.get("/")
async def root(): return {"status": "The Beast is Alive"}

@app.get("/bot/toggle")
async def toggle():
    # كود تفعيل البوت المعتاد
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    return {"status": "Running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
