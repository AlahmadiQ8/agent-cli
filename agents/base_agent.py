from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

class ResponseMessage(BaseModel):
    """Represents a single message from an agent"""
    
    role: str = Field(..., description="role: assistant or tool_call")
    content: str = Field(..., description="content")
    agent_name: Optional[str] = Field(default=None, description="Agent name for tool calls")
    tool_name: Optional[str] = Field(default=None, description="Tool name for tool calls")

    def __repr__(self) -> str:
        if self.role == "tool_call":
            return f"Message(role='{self.role}', agent='{self.agent_name}', tool='{self.tool_name}', content='{self.content[:50]}...')"
        return f"Message(role='{self.role}', content='{self.content[:50]}...')"

class BaseAgent(ABC):
    """Abstract base class for AI agents"""

    def __init__(self, name: str = "Agent"):
        self.name = name

    @abstractmethod
    async def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history"""
        pass

    @abstractmethod
    async def get_conversation_history(self) -> List[ResponseMessage]:
        """Get conversation history as list of dictionaries"""
        pass

    @abstractmethod
    async def get_recent_messages(self, count: int = 10) -> List[ResponseMessage]:
        """Get the most recent messages from conversation history"""
        pass

    @abstractmethod
    async def clear_conversation_history(self) -> None:
        """Clear all conversation history"""
        pass

    @abstractmethod
    async def get_conversation_length(self) -> int:
        """Get the number of messages in conversation history"""
        pass

    @abstractmethod
    async def generate_response(self, user_input: str) -> List[ResponseMessage]:
        """Generate a response to user input as a list of ResponseMessage objects"""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent (e.g., load model, connect to API)"""
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metadata"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close agent resources and cleanup"""
        pass

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()