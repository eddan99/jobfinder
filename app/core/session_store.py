import uuid
from app.models.domain import UserProfile


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, tuple[UserProfile, str]] = {}

    def create(self, initial_buffer: str = "") -> tuple[str, UserProfile]:
        session_id = str(uuid.uuid4())
        profile = UserProfile()
        self._sessions[session_id] = (profile, initial_buffer)
        return session_id, profile

    def get(self, session_id: str) -> tuple[UserProfile, str]:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Session not found: {session_id}")
        return session

    def append_to_buffer(self, session_id: str, text: str) -> str:
        profile, buffer = self.get(session_id)
        updated_buffer = buffer + "\n" + text
        self._sessions[session_id] = (profile, updated_buffer)
        return updated_buffer

    def update_profile(self, session_id: str, profile: UserProfile) -> None:
        _, buffer = self.get(session_id)
        self._sessions[session_id] = (profile, buffer)


session_store = SessionStore()
