from app.core.config import get_settings
from app.models.domain import UserProfile
from app.models.schemas import JobMatchResult
from app.repositories.job_repository import JobRepository
from app.services.embedding_service import EmbeddingService


class MatchmakingService:
    def __init__(self) -> None:
        self._repo = JobRepository()
        self._embedder = EmbeddingService()

    def match(self, profile: UserProfile) -> list[JobMatchResult]:
        profile_text = f"{profile.current_role} {' '.join(profile.skills)} {profile.preferred_location}"
        profile_vector = self._embedder.embed(profile_text)

        candidates = self._repo.find_nearest_by_location(
            city=profile.preferred_location,
            query_vector=profile_vector,
        )

        threshold = get_settings().match_threshold

        results = []
        for job in candidates:
            score = round(1 - job["distance"], 4)
            if score >= threshold:
                results.append(JobMatchResult(
                    title=job["role"],
                    short_description=job["description"][:300],
                    employer_name=job["employer_name"],
                    location=job["location"],
                    job_url=job["job_url"],
                    score=score,
                ))
        return results
