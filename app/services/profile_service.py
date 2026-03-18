from app.models.domain import MANDATORY_FIELDS, UserProfile


class ProfileService:
    def missing_fields(self, profile: UserProfile) -> list[str]:
        missing = []
        for field in MANDATORY_FIELDS:
            value = getattr(profile, field)
            if not value:
                missing.append(field)
        return missing

    def merge(self, existing: UserProfile, incoming: UserProfile) -> UserProfile:
        for field in vars(existing):
            incoming_value = getattr(incoming, field)
            if incoming_value:
                setattr(existing, field, incoming_value)
        existing.is_complete = not self.missing_fields(existing)
        return existing
