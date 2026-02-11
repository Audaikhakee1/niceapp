import os
import asyncio
import random
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = FastAPI()

# تفعيل CORS للاتصال بالواجهة
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- إعدادات البوت ---
TOKEN = 8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs "ضغ_هنا_توكن_البوت_الخاص_بك" # استبدله بالتوكن الحقيقي
bot_running = False
application = None

# أوامر تلجرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً أيها القائد! أنا بوت الوحش الرقمي، أعمل الآن تحت سيطرتك.")

# دالة لتشغيل البوت في الخلفية
async def run_telegram_bot():
    global application, bot_running
    if not application:
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        await application.initialize()
    
    await application.start()
    await application.updater.start_polling()
    bot_running = True
    print("Telegram Bot is Running...")

# دالة لإيقاف البوت
async def stop_telegram_bot():
    global application, bot_running
    if application:
        await application.updater.stop()
        await application.stop()
        bot_running = False
        print("Telegram Bot Stopped.")

# --- مسارات FastAPI ---

@app.get("/")
async def root():
    return {"message": "Server is Online", "bot_status": "Running" if bot_running else "Stopped"}

@app.get("/stats")
async def get_stats():
    return {"cpu": random.randint(15, 85), "ram": random.randint(30, 70)}

@app.get("/bot/toggle")
async def toggle_bot():
    global bot_running
    if not bot_running:
        asyncio.create_task(run_telegram_bot())
        return {"message": "تم إرسال أمر التشغيل للبوت", "status": "Running"}
    else:
        asyncio.create_task(stop_telegram_bot())
        return {"message": "تم إرسال أمر الإيقاف", "status": "Stopped"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

