import os
import asyncio
import random
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

app = FastAPI()

# تفعيل الـ CORS بشكل كامل
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# الإعدادات
TELEGRAM_TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs"
GEMINI_API_KEY = "AIzaSyA9OpSJAz2nE7dBc7DylYz6_LHId-u28ck"

# محاولة إعداد الذكاء الاصطناعي
try:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"AI Configuration Error: {e}")

bot_running = False
application = None
chats_memory = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_id = update.effective_user.id
    user_text = update.message.text
    try:
        if user_id not in chats_memory:
            chats_memory[user_id] = ai_model.start_chat(history=[])
        chat_session = chats_memory[user_id]
        response = chat_session.send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("عذراً، عقلي يمر بعملية تحديث. سأعود قريباً!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! الوحش الرقمي يعمل الآن بالذكاء الاصطناعي.")

@app.get("/stats")
async def get_stats():
    return {"cpu": random.randint(15, 65), "ram": random.randint(25, 55)}

@app.get("/bot/toggle")
async def toggle_bot():
    global application, bot_running
    if not bot_running:
        try:
            application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            bot_running = True
            return {"message": "تم الإيقاظ", "status": "Running"}
        except Exception as e:
            return {"message": f"فشل: {str(e)}", "status": "Stopped"}
    else:
        # كود الإيقاف
        bot_running = False
        return {"message": "تم التوقف", "status": "Stopped"}

@app.get("/")
async def root():
    return {"status": "Alive"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
