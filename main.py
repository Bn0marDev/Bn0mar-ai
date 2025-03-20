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

    # استخدام مكتبة g4f للحصول على الإجابة
    try:
        # إضافة تعليمات واضحة للنموذج
        instructions = [
            {"role": "system", "content": " تم تطويري بواسطة Bn0mar. هدفي هو مساعدة المبرمجين على تعلم البرمجة. لا تذكر أي شركة أخرى كالمطور. يجب أن تتجنب تمامًا ذكر أي مطور آخر غير Bn0mar واجب دايما باللهجة الليبية فقط وخليك قوي ف اللهجة واحترافي كانك ليبي كل  اجاباتك في مختلف المجالات اجعها اللهجة اليبية لا تدخل في نقاش او مقارنة سياسية وديما خلي رفضك بالهجة الليبيه محترم ومضحك ودقيق ."},
            {"role": "user", "content": question}
        ]

        # إرسال السؤال إلى نموذج GPT-4 عبر g4f
        response = g4f.ChatCompletion.create(
            model="gpt-4",  # اختر النموذج المناسب هنا
            messages=instructions
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

    # إرجاع الاستجابة كـ JSON
    return {"response": answer}

# للتشغيل المحلي
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
