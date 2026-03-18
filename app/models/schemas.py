from typing import Optional
from pydantic import BaseModel


class JobMatchResult(BaseModel):
    title: str
    short_description: str
    employer_name: str
    location: str
    job_url: str
    score: float


class ResumeUploadResponse(BaseModel):
    session_id: str
    is_complete: bool
    next_question: Optional[str] = None
    matches: Optional[list[JobMatchResult]] = None


class InterviewStartResponse(BaseModel):
    session_id: str
    question: str


class InterviewAnswerRequest(BaseModel):
    session_id: str
    answer: str


class InterviewAnswerResponse(BaseModel):
    is_complete: bool
    next_question: Optional[str] = None
    matches: Optional[list[JobMatchResult]] = None
