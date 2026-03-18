import re

_REMOTE_PATTERN = re.compile(
    r"\b(remote|distansarbete|hemifrån|hybridarbete|hybrid)\b", re.IGNORECASE
)


class MetadataService:
    def is_remote(self, description: str) -> bool:
        return bool(_REMOTE_PATTERN.search(description))
