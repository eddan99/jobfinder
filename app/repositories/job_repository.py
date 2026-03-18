from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector

from app.core.config import get_settings
from app.models.domain import JobListing


class JobRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._db = firestore.Client()
        self._collection = settings.firestore_collection_jobs

    def save(self, job: JobListing) -> None:
        self._db.collection(self._collection).document(job.id).set({
            "role": job.role,
            "description": job.description,
            "location": job.location,
            "remote_allowed": job.remote_allowed,
            "job_url": job.job_url,
            "employer_name": job.employer_name,
            "publication_date": job.publication_date.isoformat(),
            "embedding": Vector(job.embedding),
        })

    def find_nearest_by_location(
        self, city: str, query_vector: list[float], limit: int = 10
    ) -> list[dict]:
        results = (
            self._db.collection(self._collection)
            .where("location", "==", city)
            .find_nearest(
                vector_field="embedding",
                query_vector=Vector(query_vector),
                distance_measure=DistanceMeasure.COSINE,
                limit=limit,
                distance_result_field="distance",
            )
            .stream()
        )
        return [doc.to_dict() | {"id": doc.id} for doc in results]
