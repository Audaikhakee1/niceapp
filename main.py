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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- المفاتيح (تأكد من صحتها تماماً) ---
TELEGRAM_TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs"
GEMINI_API_KEY = "AIzaSyA9OpSJAz2nE7dBc7DylYz6_LHId-u28ck"

# محاولة تهيئة النموذج بأكثر من نسخة لضمان النجاح
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_response(prompt):
    # استخدام المسمى الخام الأحدث الذي يدعم كافة النسخ
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest') 
    response = model.generate_content(prompt)
    return response.text

chats_memory = {}
bot_running = False
application = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_text = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # محاولة الحصول على رد
        response_text = get_ai_response(user_text)
        await update.message.reply_text(response_text)
        
    except Exception as e:
        full_error = str(e)
        print(f"DEBUG ERROR: {full_error}")
        
        # إذا استمر الخطأ، سنرسل لك "كود العطل" لتعطيه لنا
        if "403" in full_error:
            msg = "🚫 خطأ 403: جوجل ترفض التوكن أو الموقع. تأكد من تفعيل Gemini في AI Studio."
        elif "429" in full_error:
            msg = "⏳ خطأ 429: حصة الرسائل المجانية انتهت مؤقتاً."
        else:
            msg = f"🔍 تقرير العطل التقني: {full_error[:100]}" # يرسل أول 100 حرف من الخطأ
            
        await update.message.reply_text(msg)

@app.get("/stats")
async def get_stats():
    return {"cpu": random.randint(10, 50), "ram": random.randint(20, 40)}

@app.get("/bot/toggle")
async def toggle_bot():
    global application, bot_running
    if not bot_running:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("الوحش استيقظ! جرب محادثتي الآن.")))
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


