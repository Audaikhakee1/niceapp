import os
import asyncio
import random
import uvicorn
import httpx  # سنستخدم هذا بدلاً من مكتبة جوجل المعطلة
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- المفاتيح ---
TELEGRAM_TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs"
GEMINI_API_KEY = "AIzaSyA9OpSJAz2nE7dBc7DylYz6_LHId-u28ck"

async def get_ai_response_direct(prompt):
    # رابط الاتصال المباشر بـ Google Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        result = response.json()
        
        # استخراج النص من الرد الخام
        try:
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return f"عذراً أيها القائد، جوجل ردت بـ: {result.get('error', {}).get('message', 'خطأ غير معروف')}"

bot_running = False
application = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # جلب الرد عبر الاتصال المباشر
    answer = await get_ai_response_direct(user_text)
    await update.message.reply_text(answer)

@app.get("/stats")
async def get_stats():
    return {"cpu": random.randint(10, 50), "ram": random.randint(20, 40)}

@app.get("/bot/toggle")
async def toggle_bot():
    global application, bot_running
    if not bot_running:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("الوحش استيقظ بنظام الاتصال المباشر!")))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        bot_running = True
        return {"status": "Running"}
    return {"status": "Active"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
