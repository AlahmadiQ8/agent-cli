from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Message:
    """Represents a single message in the conversation"""
    
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format"""
        return {"role": self.role, "content": self.content}
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Message":
        """Create message from dictionary"""
        return cls(role=data["role"], content=data["content"])
    
    def __repr__(self) -> str:
        return f"Message(role='{self.role}', content='{self.content[:50]}...')"


class BaseAgent(ABC):
    """Abstract base class for AI agents"""

    def __init__(self, name: str = "Agent"):
        self.name = name
        self.conversation_history: List[Message] = []

    async def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        message = Message(role=role, content=content)
        self.conversation_history.append(message)

    async def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history"""
        await self.add_message("user", content)

    async def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history"""
        await self.add_message("assistant", content)

    async def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history as list of dictionaries"""
        return [message.to_dict() for message in self.conversation_history]

    async def get_recent_messages(self, count: int = 10) -> List[Dict[str, str]]:
        """Get the most recent messages from conversation history"""
        recent = self.conversation_history[-count:] if count > 0 else self.conversation_history
        return [message.to_dict() for message in recent]

    async def clear_conversation_history(self) -> None:
        """Clear all conversation history"""
        self.conversation_history.clear()

    async def get_conversation_length(self) -> int:
        """Get the number of messages in conversation history"""
        return len(self.conversation_history)

    @abstractmethod
    async def generate_response(self) -> str:
        """Generate a response to user input"""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent (e.g., load model, connect to API)"""
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metadata"""
        pass