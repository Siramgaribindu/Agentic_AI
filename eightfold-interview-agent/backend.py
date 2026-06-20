from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)

app = FastAPI(
    title="AI Interview Coach",
    description="Interview Simulation using Groq"
)


class ChatMessage(BaseModel):
    role: str
    content: str


class InterviewPayload(BaseModel):
    role_name: str
    difficulty: str
    stage: str
    history: List[ChatMessage]


@app.post("/api/interview/next-question")
async def get_next_question(payload: InterviewPayload):
    try:

        system_prompt = f"""
You are an experienced technical interviewer.

Candidate Role: {payload.role_name}
Difficulty: {payload.difficulty}
Current Stage: {payload.stage}

Rules:
- Ask exactly ONE question.
- Do not ask multiple questions.
- Be professional.
- Never repeat previous questions.
- Use the conversation history.

INTRO:
Ask an introduction/background question.

TECHNICAL_1:
Ask a core technical question relevant to the role.

TECHNICAL_2:
Ask a scenario-based technical question.

BEHAVIORAL:
Ask a STAR-method behavioral question.
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        for msg in payload.history:
            if msg.role == "assistant":
                role = "assistant"
            else:
                role = "user"

            messages.append(
                {
                    "role": role,
                    "content": msg.content
                }
            )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )

        return {
            "response": completion.choices[0].message.content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interview/generate-scorecard")
async def generate_scorecard(payload: InterviewPayload):
    try:

        transcript = ""

        for msg in payload.history:
            transcript += f"{msg.role}: {msg.content}\n"

        prompt = f"""
You are a senior hiring panel.

Analyze the following interview transcript:

{transcript}

Generate a detailed INTERVIEW PERFORMANCE SCORECARD.

Include:

1. Technical Skills Score (0-100)
2. Communication Score (0-100)
3. Problem Solving Score (0-100)
4. Strengths
5. Areas for Improvement
6. Final Hiring Recommendation

Use markdown tables.
"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=1000
        )

        return {
            "scorecard": completion.choices[0].message.content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))