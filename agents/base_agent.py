from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in the conversation"""
    
    role: str = Field(..., description="Message role: user, assistant, or tool_call")
    content: str = Field(..., description="Message content")
    agent_name: Optional[str] = Field(default=None, description="Agent name for tool calls")
    tool_name: Optional[str] = Field(default=None, description="Tool name for tool calls")
    
    def __repr__(self) -> str:
        if self.role == "tool_call":
            return f"Message(role='{self.role}', agent='{self.agent_name}', tool='{self.tool_name}', content='{self.content[:50]}...')"
        return f"Message(role='{self.role}', content='{self.content[:50]}...')"


class ResponseMessage(BaseModel):
    """Represents a single response message from an agent"""
    
    role: str = Field(..., description="Response role: assistant or tool_call")
    content: str = Field(..., description="Response content")
    agent_name: Optional[str] = Field(default=None, description="Agent name for tool calls")
    tool_name: Optional[str] = Field(default=None, description="Tool name for tool calls")


class BaseAgent(ABC):
    """Abstract base class for AI agents"""

    def __init__(self, name: str = "Agent"):
        self.name = name
        self.conversation_history: List[Message] = []

    async def add_message(self, role: str, content: str, agent_name: Optional[str] = None, tool_name: Optional[str] = None) -> None:
        """Add a message to the conversation history"""
        message = Message(role=role, content=content, agent_name=agent_name, tool_name=tool_name)
        self.conversation_history.append(message)

    async def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history"""
        await self.add_message("user", content)

    async def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history"""
        await self.add_message("assistant", content)

    async def add_tool_call_message(self, content: str, agent_name: str, tool_name: str) -> None:
        """Add a tool call message to the conversation history"""
        await self.add_message("tool_call", content, agent_name=agent_name, tool_name=tool_name)

    async def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history as list of dictionaries"""
        return [message.model_dump() for message in self.conversation_history]

    async def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent messages from conversation history"""
        recent = self.conversation_history[-count:] if count > 0 else self.conversation_history
        return [message.model_dump() for message in recent]

    async def clear_conversation_history(self) -> None:
        """Clear all conversation history"""
        self.conversation_history.clear()

    async def get_conversation_length(self) -> int:
        """Get the number of messages in conversation history"""
        return len(self.conversation_history)

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