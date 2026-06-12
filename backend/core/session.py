from langchain_core.messages import HumanMessage, AIMessage

from backend.models.interaction import Interaction
from tools.agent import Agent
from tools.validator import validator


class Session:
    interactions: list[Interaction]
    agent: Agent

    def __init__(self, user_id):
        self.user_id = user_id
        self.interactions = []
        self.agent = Agent(name="Default Agent", description="This is a default agent.")

    def _build_history(self):
        history = []
        for interaction in self.interactions:
            history.append(HumanMessage(content=interaction.user_message))
            if interaction.agent_reply:
                history.append(AIMessage(content=interaction.agent_reply))
        return history

    def generate_reply(self, message):
        history = self._build_history()
        response = self.agent.invoke(message, history=history)
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[-1]
            response = response.rsplit("```", 1)[0].strip()
        data = validator.validate_agent_response(response)
        reply = data.get("reply", "Sorry, I didn't understand that.")
        end_chat = data.get("end_chat", False)
        interaction = Interaction(user_message=message, agent_reply=reply, end_chat=end_chat)
        validator.validate_interaction(interaction)
        return interaction