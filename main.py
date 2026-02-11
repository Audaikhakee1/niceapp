import os
import asyncio
import random
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = FastAPI()

# تفعيل CORS لضمان اتصال واجهة التحكم (index.html) بالسيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- إعدادات البوت الحقيقية ---
TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs" 
bot_running = False
application = None

# أوامر تلجرام: ماذا سيفعل البوت عند كتابة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"مرحباً يا {user_name}! أنا بوت الوحش الرقمي. تم تفعيل نظام التحكم عن بعد بنجاح. 🚀")

# دالة تشغيل البوت في الخلفية (Background Task)
async def run_telegram_bot():
    global application, bot_running
    try:
        if not application:
            application = ApplicationBuilder().token(TOKEN).build()
            application.add_handler(CommandHandler("start", start))
            await application.initialize()
        
        await application.start()
        await application.updater.start_polling()
        bot_running = True
        print("Telegram Bot is Online!")
    except Exception as e:
        print(f"Error starting bot: {e}")
        bot_running = False

# دالة إيقاف البوت
async def stop_telegram_bot():
    global application, bot_running
    if application:
        await application.updater.stop()
        await application.stop()
        bot_running = False
        print("Telegram Bot Offline.")

# --- مسارات التحكم (Endpoints) ---

@app.get("/")
async def root():
    return {"status": "Online", "bot": "Running" if bot_running else "Stopped"}

@app.get("/stats")
async def get_stats():
    # بيانات وهمية لتغذية الرسم البياني في index.html
    return {"cpu": random.randint(10, 90), "ram": random.randint(20, 80)}

@app.get("/bot/toggle")
async def toggle_bot():
    global bot_running
    if not bot_running:
        asyncio.create_task(run_telegram_bot())
        return {"message": "جاري إيقاظ البوت...", "status": "Running"}
    else:
        asyncio.create_task(stop_telegram_bot())
        return {"message": "تم إرسال أمر النوم للبوت", "status": "Stopped"}

if __name__ == "__main__":
    # Railway يحدد المنفذ تلقائياً
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
