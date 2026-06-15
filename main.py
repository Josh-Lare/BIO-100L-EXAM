from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import requests
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("Bio 101 questions_db.json", "r") as file:
    QUESTIONS_DB = json.load(file)

class ExamSubmission(BaseModel):
    name: str
    matric: str
    dept: str
    answers: List[Optional[str]]

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbxO0dpsIvdHp-OZ8zF6g1FcTBSRzH4DEhrxjaUDUQvl4b6-DFhoymMRYllJXmIgWMTH/exec"

@app.get("/api/questions")
def get_secure_questions():
    safe_questions = []
    for q in QUESTIONS_DB:
        safe_q = {"n": q["n"], "topic": q["topic"], "q": q["q"], "opts": q["opts"]}
        safe_questions.append(safe_q)
    return safe_questions

@app.post("/api/submit")
def grade_exam(submission: ExamSubmission):
    correct = 0
    wrong = 0
    skipped = 0

    for i, user_answer in enumerate(submission.answers):
        actual_answer = QUESTIONS_DB[i]["ans"]
        if user_answer is None:
            skipped += 1
        elif user_answer == actual_answer:
            correct += 1
        else:
            wrong += 1

    total_questions = len(QUESTIONS_DB)
    pct = round((correct / total_questions) * 100)

    if pct >= 70: grade = 'First Class (A)'
    elif pct >= 60: grade = 'Second Class Upper (B)'
    elif pct >= 50: grade = 'Second Class Lower (C)'
    elif pct >= 45: grade = 'Third Class (D)'
    else: grade = 'Fail (F)'

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "timestamp": current_time,
        "name": submission.name,
        "matric": submission.matric,
        "dept": submission.dept,
        "score": correct,
        "percentage": f"{pct}%",
        "grade": grade
    }

    # ── FIXED: try block was missing, variable name was wrong ──
    try:
        response = requests.post(GOOGLE_SHEET_URL, json=payload)  # was: json=data
        print(f"DEBUG: Google responded with: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to save to Google Sheets: {e}")

    # ── Always return the result to the student regardless ──
    return {
        "student": submission.name,
        "matric": submission.matric,
        "score": correct,
        "percentage": pct,
        "grade": grade,

        @app.get("/")
def serve_frontend():
    return FileResponse("index.html")
        "stats": {"correct": correct, "wrong": wrong, "skipped": skipped}
    }
