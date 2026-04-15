from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Rasm uchun
import os

from api import api_router
from database import engine, Base # Bazani ishga tushirish uchun

# Jadvallarni yaratish (Agar mavjud bo'lmasa)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PostHub API")

# CORS sozlamalari - kengaytirilgan variant
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ishlab chiqish jarayonida hamma manzilga ruxsat
    allow_credentials=True, # Tokenlar bilan ishlash uchun muhim
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agar 'uploads' degan papkada rasmlar saqlansa, ularni ko'rish uchun:
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routerni ulash
app.include_router(api_router)

@app.get("/")
def home():
    return {"message": "PostHub API ishlamoqda", "docs": "/docs"}