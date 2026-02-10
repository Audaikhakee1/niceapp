from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# هذا المسار سيقبل أي شيء وكل شيء (GET)
@app.get("/deploy")
async def deploy(type: str = "test"):
    return {"message": f"تم استلام أمر: {type}", "status": "Success"}

@app.get("/")
async def root():
    return {"message": "Engine is Online"}
