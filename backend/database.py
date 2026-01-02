# backend/database.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 数据库（文件会自动创建在 backend 目录下）
ENGINE = create_engine('sqlite:///japanese_phrases.db', echo=False, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

Base = declarative_base()

# backend/database.py
class Phrase(Base):
    __tablename__ = "phrases"

    id = Column(Integer, primary_key=True, index=True)
    japanese = Column(String, nullable=False)
    romaji = Column(String, nullable=False)
    english = Column(String, nullable=False)
    hiragana = Column(String, nullable=False)  # 新增：平假名版本，用于准确比对

# 创建表（第一次运行时）
def init_db():
    Base.metadata.create_all(bind=ENGINE)