from backend.models.interaction import Interaction


class Session:
    interactions: list[Interaction]

    def __init__(self, user_id):
        self.user_id = user_id
        self.interactions = []

    def generate_reply(self, message):
        # Placeholder for actual reply generation logic
        reply = f"Echo: {message}"
        return Interaction(user_message=message, agent_reply=reply)