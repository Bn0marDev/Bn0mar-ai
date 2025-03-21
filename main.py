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
        # إرسال السؤال إلى نموذج GPT-4 عبر gf4
        response = g4f.ChatCompletion.create(
            model="gpt-4o",  # اختر النموذج المناسب هنا
            messages=[{"role": "user", "content": question}]
        )
        
        # طباعة الاستجابة للتصحيح
        print("Response:", response)

        # التعامل مع الاستجابة بشكل صحيح
        # g4f يمكن أن يعيد استجابة كنص مباشرة أو كائن
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

    # إضافة تعليمات باللهجة الليبية
    libyan_response = f"{answer} \n\nأنا تم تطويري بواسطة Bn0mar. إذا كنت تحتاج أي مساعدة أو تواصل، تقدر تتواصل معايا عبر: \n\nتيك توك: m0usa_0mar\nفيسبوك: https://www.facebook.com/mousa.0mar"

    # إرجاع الاستجابة باللهجة الليبية
    return {"response": libyan_response}

# للتشغيل المحلي
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
