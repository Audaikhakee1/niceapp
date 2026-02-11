import os
import uvicorn
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# تفعيل تصريح العبور (CORS) لضمان اتصال الواجهة بالسيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "The Beast is Alive on Railway!", "status": "Secure"}

# المحرك الذي يغذي الرسم البياني بالبيانات
@app.get("/stats")
async def get_stats():
    return {
        "cpu": random.randint(20, 80),
        "ram": random.randint(40, 75)
    }

# مسار تنفيذ الأوامر من الأزرار
@app.get("/deploy")
async def deploy(type: str = "Unknown"):
    return {"message": f"تم استلام أمر: {type}", "status": "Success"}

if __name__ == "__main__":
    # الحصول على المنفذ تلقائياً من Railway
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
