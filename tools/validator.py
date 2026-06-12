import json

class Validator:
    def validate_interaction(self, interaction):
        if not interaction.user_message:
            raise ValueError("User message cannot be empty.")
        if interaction.agent_reply is not None and not isinstance(interaction.agent_reply, str):
            raise ValueError("Agent reply must be a string or None.")
        if not isinstance(interaction.end_chat, bool):
            raise ValueError("end_chat must be a boolean.")
        
    def validate_session(self, session):
        if not session.user_id:
            raise ValueError("Session must have a user_id.")
        if not isinstance(session.interactions, list):
            raise ValueError("Session interactions must be a list.")
        for interaction in session.interactions:
            self.validate_interaction(interaction)

    def validate_agent_response(self, response):
        if not isinstance(response, str):
            raise ValueError("Agent response must be a string.")
        try:
            data = json.loads(response)
            if "reply" not in data:
                raise ValueError("Agent response JSON must contain a 'reply' field.")
            if not isinstance(data["reply"], str):
                raise ValueError("The 'reply' field in agent response must be a string.")
            if "end_chat" in data and not isinstance(data["end_chat"], bool):
                raise ValueError("The 'end_chat' field in agent response must be a boolean if present.")
            return data
        except json.JSONDecodeError:
            raise ValueError("Agent response must be a valid JSON string.")
        

validator = Validator()