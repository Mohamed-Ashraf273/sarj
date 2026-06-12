from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

from config import config
from tools.sarj_search import SarjSearch


class Agent:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.tools = [SarjSearch()]
        self.llm = ChatAnthropic(
            model=config.MODEL,
            temperature=config.TEMPERATURE,
            anthropic_api_key=config.ANTHROPIC_API_KEY,
        )
        system_prompt = (
            f"You are {self.name}. {self.description}\n"
            "Always respond in JSON format with two fields:\n"
            '  "reply": string — your response to the user\n'
            '  "end_chat": bool — true only if the conversation should end\n'
            "Do not include anything outside the JSON object."
        )
        self._agent = create_agent(
            self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )

    def __str__(self):
        return f"Agent(name={self.name}, description={self.description})"

    def invoke(self, message, history: list = None):
        chat_history = history or []
        result = self._agent.invoke({
            "messages": chat_history + [HumanMessage(content=message)],
        })
        content = result["messages"][-1].content
        # Claude returns content as a list of blocks; extract text
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        return content
     