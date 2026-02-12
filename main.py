import os
import asyncio
import random
import uvicorn
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- البيانات السرية ---
TELEGRAM_TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs"
GEMINI_API_KEY = "AIzaSyA9OpSJAz2nE7dBc7DylYz6_LHId-u28ck"

async def ask_gemini(prompt):
    """محرك الاستعلام المباشر - يتجاوز تعقيدات المكتبات"""
    # جربنا v1beta و v1 وفشلا، الآن سنستخدم الرابط العالمي المباشر
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=25.0)
            data = response.json()
            
            # فحص النجاح
            if response.status_code == 200 and 'candidates' in data:
                return data['candidates'][0]['content']['parts'][0]['text']
            
            # فحص نوع الخطأ بدقة هندسية
            error_status = data.get('error', {}).get('status', 'Unknown')
            error_message = data.get('error', {}).get('message', 'No message')
            
            if "LOCATION" in error_message or "supported" in error_message:
                return "⚠️ الوحش يعمل، لكن جوجل تحظر منطقة السيرفر (Railway Region). سأقوم بتفعيل نظام البروكسي لاحقاً."
            
            return f"❌ خطأ تقني ({error_status}): {error_message[:50]}"
            
        except Exception as e:
            return f"⚙️ عطل في نظام الاتصال: {str(e)[:30]}"

# --- منطق البوت والواجهة ---
bot_running = False
application = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # تنفيذ الاستعلام
    reply = await ask_gemini(update.message.text)
    await update.message.reply_text(reply)

@app.get("/stats")
async def get_stats():
    return {"cpu": random.randint(10, 60), "ram": random.randint(20, 50)}

@app.get("/bot/toggle")
async def toggle_bot():
    global application, bot_running
    if not bot_running:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("الوحش الرقمي جاهز للخدمة، أرسل رسالتك.")))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        bot_running = True
        return {"status": "Running"}
    return {"status": "Online"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
