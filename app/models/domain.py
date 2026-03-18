from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

MANDATORY_FIELDS = ["full_name", "current_role", "preferred_location", "skills"]


@dataclass
class UserProfile:
    full_name: Optional[str] = None
    current_role: Optional[str] = None
    preferred_location: Optional[str] = None
    skills: list[str] = field(default_factory=list)
    seniority: Optional[str] = None
    experience_years: Optional[int] = None
    is_complete: bool = False


@dataclass
class JobListing:
    id: str
    role: str
    description: str
    location: str
    remote_allowed: bool
    job_url: str
    employer_name: str
    publication_date: datetime
    embedding: list[float] = field(default_factory=list)
