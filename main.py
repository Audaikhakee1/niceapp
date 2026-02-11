import os
import asyncio
import random
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات الأساسية ---
TELEGRAM_TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs"
GEMINI_API_KEY = "AIzaSyA9OpSJAz2nE7dBc7DylYz6_LHId-u28ck"

# إعداد الذكاء الاصطناعي
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

bot_running = False
application = None

# --- منطق الذكاء الاصطناعي ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_text = update.message.text
    # إرسال إشارة "جاري الكتابة" لإضفاء طابع واقعي
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # صياغة شخصية البوت (System Prompt)
        prompt = f"أنت 'الوحش الرقمي'، بوت ذكي وقوي يدير سيرفر القائد. أجب باختصار وذكاء بلهجة تقنية محترفة على: {user_text}"
        response = ai_model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("عذراً، عقلي يمر بعملية تحديث لحظية. حاول ثانية!")

# --- أوامر البوت المعتادة ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم تفعيل 'الوحش الرقمي'. أنا الآن مزود بالذكاء الاصطناعي، اسألني أي شيء عن سيرفرك أو عن العالم!")

# --- إدارة تشغيل البوت ---
async def run_bot():
    global application, bot_running
    if not application:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        # جعل البوت يرد على أي رسالة نصية باستخدام الذكاء الاصطناعي
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        await application.initialize()
    await application.start()
    await application.updater.start_polling()
    bot_running = True

async def stop_bot():
    global application, bot_running
    if application:
        await application.updater.stop()
        await application.stop()
        bot_running = False

# --- مسارات FastAPI للوحة التحكم ---
@app.get("/stats")
async def get_stats():
    return {"cpu": random.randint(20, 70), "ram": random.randint(30, 60)}

@app.get("/bot/toggle")
async def toggle_bot():
    global bot_running
    if not bot_running:
        asyncio.create_task(run_bot())
        return {"message": "تم إيقاظ عقل الوحش بنجاح", "status": "Running"}
    else:
        asyncio.create_task(stop_bot())
        return {"message": "الوحش الآن في وضع النوم العميق", "status": "Stopped"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
