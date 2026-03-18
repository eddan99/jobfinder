import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.core.session_store import session_store
from app.models.schemas import ResumeUploadResponse
from app.services.llm_service import LLMService
from app.services.matchmaking_service import MatchmakingService
from app.services.profile_service import ProfileService
from app.services.resume_parser import ResumeParser

router = APIRouter()

_parser = ResumeParser()
_llm = LLMService()
_profile_service = ProfileService()
_matchmaking = MatchmakingService()

_ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile) -> ResumeUploadResponse:
    suffix = Path(file.filename).suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    parsed_text = _parser.parse(tmp_path)
    tmp_path.unlink()

    session_id, empty_profile = session_store.create(initial_buffer=parsed_text)
    extracted_profile, next_question = await _llm.extract_and_ask(parsed_text)
    merged_profile = _profile_service.merge(empty_profile, extracted_profile)
    session_store.update_profile(session_id, merged_profile)

    return ResumeUploadResponse(
        session_id=session_id,
        is_complete=merged_profile.is_complete,
        next_question=next_question,
        matches=_matchmaking.match(merged_profile) if merged_profile.is_complete else None,
    )
