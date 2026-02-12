import os
import uvicorn
import httpx
from fastapi import FastAPI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

app = FastAPI()

# الإعدادات الأساسية
TELEGRAM_TOKEN = "8123154181:AAEZinaf1XcMDyuXgebGJeC0NoHsw-a7yIs"
ADMIN_ID = 7955469863
KIMI_KEY = "sk-zo0vcFZSzR6lW3fe4tua6TDgkIRB2ZNM0gkY7scikzV4CicL"

async def ask_ai(prompt):
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {"Authorization": f"Bearer {KIMI_KEY}", "Content-Type": "application/json"}
    payload = {"model": "moonshot-v1-8k", "messages": [{"role": "user", "content": prompt}]}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=20.0)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return f"⚠️ المحرك متعب (كود {response.status_code})"
        except:
            return "⚙️ النفق الرقمي مغلق حالياً."

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID: return
    await u.message.reply_text(await ask_ai(u.message.text))

@app.get("/")
async def status(): return {"message": "The Beast Never Dies"}

@app.get("/bot/start")
async def start_bot():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    await app_bot.initialize()
    await app_bot.start()
    await app_bot.updater.start_polling()
    return {"status": "Back to Life"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
