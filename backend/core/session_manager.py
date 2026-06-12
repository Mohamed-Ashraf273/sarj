from backend.core.session import Session
from backend.models.interaction import Interaction
from tools.validator import validator

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self):
        user_id = f"user_{len(self.sessions) + 1}"
        session = Session(user_id)
        self.sessions[user_id] = session
        return user_id
    
    def open_session(self, user_id):
        if user_id not in self.sessions:
            raise ValueError(f"Session with user_id {user_id} does not exist.")
        session = self.sessions[user_id]
        validator.validate_session(session)
        return session

    def list_sessions(self):
        return list(self.sessions.keys())
    
    def update_session_title(self, user_id, title):
        if user_id in self.sessions:
            self.sessions[user_id].title = title

    def save_message(self, user_id, interaction: Interaction):
        if user_id in self.sessions:
            validator.validate_interaction(interaction)
            self.sessions[user_id].interactions.append(interaction)

    def close_session(self, user_id):
        if user_id in self.sessions:
            del self.sessions[user_id]


session_manager = SessionManager()