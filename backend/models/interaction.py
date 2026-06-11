from dataclasses import dataclass
from typing import Optional


@dataclass
class Interaction:
    user_message: str
    agent_reply: Optional[str] = None
    transfer: bool = False
    transfer_to: Optional[str] = None