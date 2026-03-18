import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

from app.core.config import get_settings
from app.models.domain import JobListing
from app.repositories.job_repository import JobRepository
from app.services.embedding_service import EmbeddingService
from app.services.metadata_service import MetadataService

_SPINDL_NS = "https://spindl.auranest.com/rss"


class RSSWatcher:
    def __init__(self) -> None:
        self._repo = JobRepository()
        self._embedder = EmbeddingService()
        self._metadata = MetadataService()

    def fetch_and_store(self) -> None:
        for url in get_settings().rss_feed_urls:
            xml_content = self._fetch(url)
            root = ET.fromstring(xml_content)
            for item in root.findall(".//item"):
                job = self._parse_item(item)
                if job:
                    self._repo.save(job)

    def _fetch(self, url: str) -> bytes:
        with urllib.request.urlopen(url) as response:
            return response.read()

    def _parse_item(self, item: ET.Element) -> JobListing | None:
        job_id = item.findtext("guid", "")
        title = item.findtext("title", "")
        description = item.findtext("description", "")
        job_url = item.findtext("link", "")
        employer_name = item.findtext(f"{{{_SPINDL_NS}}}employerName", "")
        city = item.findtext(f"{{{_SPINDL_NS}}}location/{{{_SPINDL_NS}}}city", "")
        pub_date_raw = item.findtext("pubDate", "")

        if not all([job_id, title, description, job_url, city]):
            return None

        try:
            publication_date = parsedate_to_datetime(pub_date_raw).replace(tzinfo=None)
        except Exception:
            publication_date = datetime.utcnow()

        remote_allowed = self._metadata.is_remote(description)
        embedding = self._embedder.embed(f"{title} {description} {city}")

        return JobListing(
            id=job_id,
            role=title,
            description=description,
            location=city,
            remote_allowed=remote_allowed,
            job_url=job_url,
            employer_name=employer_name,
            publication_date=publication_date,
            embedding=embedding,
        )
