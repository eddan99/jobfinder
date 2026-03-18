from fastapi import APIRouter, HTTPException

from app.core.session_store import session_store
from app.models.schemas import (
    InterviewAnswerRequest,
    InterviewAnswerResponse,
    InterviewStartResponse,
)
from app.services.llm_service import LLMService
from app.services.matchmaking_service import MatchmakingService
from app.services.profile_service import ProfileService

router = APIRouter()

_llm = LLMService()
_profile_service = ProfileService()
_matchmaking = MatchmakingService()

_START_PROMPT = "Hej! Låt mig hjälpa dig hitta det perfekta jobbet för dig. Vi börjar med ditt namn? :)"


@router.post("/interview/start", response_model=InterviewStartResponse)
async def start_interview() -> InterviewStartResponse:
    session_id, _ = session_store.create()
    return InterviewStartResponse(session_id=session_id, question=_START_PROMPT)


@router.post("/interview/answer", response_model=InterviewAnswerResponse)
async def answer_interview(body: InterviewAnswerRequest) -> InterviewAnswerResponse:
    try:
        existing_profile, _ = session_store.get(body.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    updated_buffer = session_store.append_to_buffer(body.session_id, body.answer)
    incoming_profile, next_question = await _llm.extract_and_ask(updated_buffer)
    merged_profile = _profile_service.merge(existing_profile, incoming_profile)
    session_store.update_profile(body.session_id, merged_profile)

    if not merged_profile.is_complete:
        return InterviewAnswerResponse(is_complete=False, next_question=next_question)

    return InterviewAnswerResponse(
        is_complete=True,
        matches=_matchmaking.match(merged_profile),
    )
