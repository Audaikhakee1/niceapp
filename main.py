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

# --- بيانات القائد والوصول ---
TELEGRAM_TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs"
GEMINI_API_KEY = "AIzaSyA9OpSJAz2nE7dBc7DylYz6_LHId-u28ck"
ADMIN_ID = 7955469863  # تم تثبيت هويتك هنا

async def ask_gemini(prompt):
    # محاولة استخدام الرابط المستقر مع نسخة v1
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=25.0)
            data = response.json()
            
            if response.status_code == 200 and 'candidates' in data:
                return data['candidates'][0]['content']['parts'][0]['text']
            
            # فحص الخطأ الجغرافي
            error_msg = data.get('error', {}).get('message', '')
            if "location" in error_msg.lower():
                return "🚨 جوجل تحظر منطقة السيرفر حالياً. القائد، نحتاج لتفعيل بروكسي أو تغيير المنطقة لـ US-Central."
            
            return f"❌ رد النظام: {error_msg[:50]}"
        except Exception as e:
            return f"⚙️ عطل اتصال: {str(e)[:30]}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # الحارس الشخصي: التحقق من الهوية
    if update.effective_user.id != ADMIN_ID:
        # البوت لن يرد حتى، سيتجاهل المتطفل تماماً لزيادة الأمان
        print(f"🚫 منع متطفل يحمل ID: {update.effective_user.id}")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await ask_gemini(update.message.text)
    await update.message.reply_text(reply)

@app.get("/stats")
async def get_stats():
    return {"cpu": random.randint(10, 40), "ram": random.randint(15, 35)}

@app.get("/bot/toggle")
async def toggle_bot():
    global application, bot_running
    # نظام التشغيل الآمن
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("الوحش استيقظ. بانتظار أوامرك أيها القائد.") if u.effective_user.id == ADMIN_ID else None))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    return {"status": "Locked & Running", "commander_id": ADMIN_ID}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
