# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random

DATABASE_URL = "sqlite:///japanese_phrases.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Phrase(Base):
    __tablename__ = "phrases"
    id = Column(Integer, primary_key=True, index=True)
    japanese = Column(String, nullable=False)
    romaji = Column(String, nullable=False)
    english = Column(String, nullable=False)
    hiragana = Column(String, nullable=False)
    category = Column(String, nullable=False, default="basic")  # 新增：课程分类

Base.metadata.create_all(bind=engine)

app = FastAPI(title="日语口语练习后端")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        if db.query(Phrase).count() == 0:
            initial_phrases = [
                # 课程1：日常问候
                {"japanese": "こんにちは", "romaji": "Konnichiwa", "english": "Hello", "hiragana": "こんにちは", "category": "greeting"},
                {"japanese": "おはようございます", "romaji": "Ohayō gozaimasu", "english": "Good morning", "hiragana": "おはようございます", "category": "greeting"},
                {"japanese": "こんばんは", "romaji": "Konbanwa", "english": "Good evening", "hiragana": "こんばんは", "category": "greeting"},
                {"japanese": "お元気ですか？", "romaji": "Ogenki desu ka?", "english": "How are you?", "hiragana": "おげんきですか", "category": "greeting"},
                {"japanese": "はい、元気です", "romaji": "Hai, genki desu", "english": "I'm fine", "hiragana": "はい、げんきです", "category": "greeting"},

                # 课程2：自我介绍
                {"japanese": "はじめまして", "romaji": "Hajimemashite", "english": "Nice to meet you", "hiragana": "はじめまして", "category": "introduction"},
                {"japanese": "私は学生です", "romaji": "Watashi wa gakusei desu", "english": "I am a student", "hiragana": "わたしはがくせいです", "category": "introduction"},
                {"japanese": "名前は何ですか？", "romaji": "Namae wa nan desu ka?", "english": "What is your name?", "hiragana": "なまえはなんですか", "category": "introduction"},
                {"japanese": "よろしくお願いします", "romaji": "Yoroshiku onegaishimasu", "english": "Please treat me well", "hiragana": "よろしくおねがいします", "category": "introduction"},

                # 课程3：感谢与道歉
                {"japanese": "ありがとうございます", "romaji": "Arigatō gozaimasu", "english": "Thank you very much", "hiragana": "ありがとうございます", "category": "thanks"},
                {"japanese": "すみません", "romaji": "Sumimasen", "english": "Excuse me / Sorry", "hiragana": "すみません", "category": "thanks"},
                {"japanese": "ごめんなさい", "romaji": "Gomen nasai", "english": "I'm sorry", "hiragana": "ごめんなさい", "category": "thanks"},
                {"japanese": "どういたしまして", "romaji": "Dōitashimashite", "english": "You're welcome", "hiragana": "どういたしまして", "category": "thanks"},
            ]
            for p in initial_phrases:
                db.add(Phrase(**p))
            db.commit()
            print("初始课程和句子已插入")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "日语口语练习后端 - 支持课程分类"}

@app.get("/categories")
def get_categories():
    db = SessionLocal()
    try:
        categories = db.query(Phrase.category).distinct().all()
        cats = [c[0] for c in categories]
        return {
            "greeting": "日常问候",
            "introduction": "自我介绍",
            "thanks": "感谢与道歉"
        }  # 可扩展更多
    finally:
        db.close()

@app.get("/phrases/{category}")
def get_phrases_by_category(category: str):
    db = SessionLocal()
    try:
        phrases = db.query(Phrase).filter(Phrase.category == category).all()
        if not phrases:
            return {"error": "课程暂无句子"}
        return [{
            "id": p.id,
            "japanese": p.japanese,
            "romaji": p.romaji,
            "english": p.english,
            "hiragana": p.hiragana
        } for p in phrases]
    finally:
        db.close()

@app.get("/get_phrase/{category}")
def get_random_phrase(category: str):
    db = SessionLocal()
    try:
        phrases = db.query(Phrase).filter(Phrase.category == category).all()
        if not phrases:
            return {"error": "该课程暂无句子"}
        selected = random.choice(phrases)
        return {
            "id": selected.id,
            "japanese": selected.japanese,
            "romaji": selected.romaji,
            "english": selected.english,
            "hiragana": selected.hiragana,
            "category": selected.category
        }
    finally:
        db.close()