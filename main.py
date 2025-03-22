from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import g4f
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text
import os
import uuid

# تعريف تطبيق FastAPI
app = FastAPI()

# إضافة CORS إلى التطبيق للسماح بالوصول من أي مصدر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # السماح لجميع المصادر
    allow_credentials=True,
    allow_methods=["*"],  # السماح بجميع الطرق مثل GET و POST
    allow_headers=["*"],  # السماح بجميع الرؤوس
)

# إعدادات قاعدة البيانات
DATABASE_URL = "postgresql://bn0mar_user:y9fKA7iXH2cNSgdj8Ic9RAjqSLHIG5gF@dpg-cvf5m43qf0us73fm54tg-a/bn0mar"

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    details = Column(Text, nullable=True)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        # إنشاء الجداول إذا لم تكن موجودة
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await init_db()

# تعريف الـ Request Body
class QuestionRequest(BaseModel):
    user_id: str
    text: str  # حقل السؤال

# تعريف الـ Endpoint الذي يستقبل السؤال
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    user_id = request.user_id
    question = request.text

    # استخدام مكتبة gf4 للحصول على الإجابة
    try:
        # إرسال السؤال إلى نموذج GPT-4-turbo عبر gf4 مع تعليمات
        response = g4f.ChatCompletion.create(
            model="gpt-4-turbo",  # استخدام النموذج المحدّث
            messages=[{
                "role": "system", 
                "content": "انت Bn0mar-ai طورك M0usaBn0ar على فهم والتكلم باللهجة الليبية وطورك لغرض مساعدة المستخدمين لحل مختلف المشاكل."
            }, {
                "role": "user", 
                "content": question
            }]
        )
        
        # طباعة الاستجابة للتصحيح
        print("Response:", response)

        # التعامل مع الاستجابة بشكل صحيح
        if isinstance(response, str):
            answer = response
        elif isinstance(response, dict):
            if 'choices' in response and len(response['choices']) > 0:
                answer = response['choices'][0]['message']['content']
            elif 'response' in response:
                answer = response['response']
            else:
                answer = str(response)  # تحويل الكائن إلى نص
        else:
            answer = str(response)  # تحويل أي نوع آخر إلى نص

        # تخزين السؤال والإجابة في قاعدة البيانات
        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_conversation = Conversation(user_id=user_id, question=question, answer=answer)
                session.add(new_conversation)
            await session.commit()

    except Exception as e:
        print(f"Error: {str(e)}")
        answer = f"حدث خطأ أثناء المعالجة: {str(e)}"

    # إرجاع الاستجابة باللهجة الليبية
    return {"response": answer}

# Endpoint لإنشاء معرف مستخدم فريد
@app.post("/create_user")
async def create_user():
    user_id = str(uuid.uuid4())
    return {"user_id": user_id}

# Endpoint لاسترجاع المحادثات السابقة لمستخدم معين
@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(sqlalchemy.select(Conversation).filter_by(user_id=user_id))
            conversations = result.scalars().all()
    return {"conversations": [{"question": c.question, "answer": c.answer, "details": c.details} for c in conversations]}

# للتشغيل المحلي
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
