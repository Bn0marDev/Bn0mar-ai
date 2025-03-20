from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import g4f

app = FastAPI()

class Question(BaseModel):
    text: str

@app.post("/ask")
async def ask_gpt(question: Question):
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": question.text}]
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "مرحبًا بك في API الدردشة باستخدام GPT-4o!"}
