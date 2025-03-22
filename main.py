from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import g4f

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

# تعريف الـ Request Body
class QuestionRequest(BaseModel):
    text: str  # حقل السؤال

# تعريف الـ Endpoint الذي يستقبل السؤال
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.text

    # استخدام مكتبة gf4 للحصول على الإجابة
    try:
        # إرسال السؤال إلى نموذج GPT-4 عبر gf4 مع تعليمات
        response = g4f.ChatCompletion.create(
            model="gemini-2.0-flash-thinking",  # اختر النموذج المناسب هنا
            messages=[{
                "role": "system", 
                "content": "انت Bn0mar-ai طورك M0usaBn0ar على فهم والتكلم باللهجة الليلية وطورك لغرض مساعدة المستخدمين لحل مختلف المشكللت التي تواججهم يمكنهم فقط الطلب لا تذكر انك طورت من قِقبل OpenAi بل ان مطورك هو الليبي Bn0mar وكن جادا ومتوسط الجدية والفكاهة وتجنب التكلم بالمصرية والتونسية واي لغة غير الليبية   لا بأس بذكر موديلك واسمك الاصلي لكن مطورك هوا Bn0mar وكن رزين الرد وليس رد غير منطقي وكن لطيفا ودودا تجعل الشخص يستمر في الدردشة معك"
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

    except Exception as e:
        print(f"Error: {str(e)}")
        answer = f"حدث خطأ أثناء المعالجة: {str(e)}"

    # إرجاع الاستجابة باللهجة الليبية
    return {"response": answer}

# للتشغيل المحلي
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
