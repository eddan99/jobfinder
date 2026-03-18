import json

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.models.domain import UserProfile

_EXTRACTION_PROMPT = """
You are a professional resume parser. Extract structured profile data from the text provided.

Return a JSON object with exactly these keys:
- full_name: string or null
- current_role: string or null
- preferred_location: the city where the person wants to work (not where they live). Look for phrases like "söker jobb i", "vill jobba i", "önskar arbeta i". If not explicitly stated, use null
- skills: array of strings
- seniority: one of "junior", "mid", "senior" or null
- experience_years: integer or null

Rules:
- Only include information explicitly stated in the text
- skills must be a list, never a string
- experience_years must be a number, never a string
- If a field cannot be determined, use null

Example output:
{
  "full_name": "Anna Svensson",
  "current_role": "Backend Developer",
  "preferred_location": "Stockholm",
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "seniority": "senior",
  "experience_years": 7
}
"""

_QUESTION_PROMPT = """
You are a warm and curious recruiter having a natural conversation in Swedish.
The user is filling in their job profile. Mandatory fields are: full_name, current_role, preferred_location, skills.

Read the conversation so far and figure out what information is still missing.
Then write a short, natural message (2-3 sentences) that:
- Reacts genuinely to something the person just said
- Varies your tone and opening — don't always start the same way
- Naturally guides toward the most important missing field

If all mandatory fields are clearly present in the text, reply with exactly: COMPLETE
"""


class LLMService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
        )
        self._model = settings.gemini_model

    async def _extract_profile_async(self, text: str) -> UserProfile:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=_EXTRACTION_PROMPT,
                temperature=0.0,
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
        return UserProfile(
            full_name=data.get("full_name"),
            current_role=data.get("current_role"),
            preferred_location=data.get("preferred_location"),
            skills=data.get("skills") or [],
            seniority=data.get("seniority"),
            experience_years=data.get("experience_years"),
        )

    async def _generate_question_async(self, text: str) -> str | None:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=_QUESTION_PROMPT,
                temperature=0.7,
            ),
        )
        result = response.text.strip()
        return None if result == "COMPLETE" else result

    async def extract_and_ask(self, text: str) -> tuple[UserProfile, str | None]:
        profile = await self._extract_profile_async(text)
        question = await self._generate_question_async(text)
        return profile, question
