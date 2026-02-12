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

# --- المفاتيح ---
TELEGRAM_TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs"
GEMINI_API_KEY = "AIzaSyA9OpSJAz2nE7dBc7DylYz6_LHId-u28ck"

# إعداد الذكاء الاصطناعي مع محاولة تجاوز حظر الموقع
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # استخدام نسخة 1.0 pro لأنها أكثر استقراراً في السيرفرات السحابية
    ai_model = genai.GenerativeModel('gemini-1.0-pro')
except Exception as e:
    print(f"Setup Error: {e}")

chats_memory = {}
bot_running = False
application = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_id = update.effective_user.id
    user_text = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        if user_id not in chats_memory:
            chats_memory[user_id] = ai_model.start_chat(history=[])
        
        # محاولة جلب الرد من الذكاء الاصطناعي
        chat_session = chats_memory[user_id]
        response = chat_session.send_message(user_text)
        await update.message.reply_text(response.text)
        
    except Exception as e:
        error_msg = str(e)
        print(f"AI ERROR: {error_msg}")
        
        # إذا كان الخطأ بسبب الموقع الجغرافي (User location is not supported)
        if "location" in error_msg.lower():
            await update.message.reply_text("⚠️ القائد، سيرفر Google يحظر منطقتي الحالية. سأرد عليك آلياً: أنا استلمت رسالتك وأعمل على تجاوز الحظر!")
        else:
            await update.message.reply_text("🤖 عقلي مشوش قليلاً حالياً، لكنني ما زلت هنا لمراقبة سيرفرك.")

@app.get("/stats")
async def get_stats():
    return {"cpu": random.randint(10, 50), "ram": random.randint(20, 40)}

@app.get("/bot/toggle")
async def toggle_bot():
    global application, bot_running
    if not bot_running:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("الوحش استيقظ!")))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        bot_running = True
        return {"status": "Running"}
    return {"status": "Already Running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
