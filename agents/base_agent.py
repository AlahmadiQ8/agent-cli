from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class Message:
    """Represents a single message in the conversation"""
    
    def __init__(self, role: str, content: str, agent_name: Optional[str] = None, tool_name: Optional[str] = None):
        self.role = role  # "user", "assistant", "tool_call"
        self.content = content
        self.agent_name = agent_name  # For tool calls
        self.tool_name = tool_name    # For tool calls
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format"""
        result = {"role": self.role, "content": self.content}
        if self.agent_name:
            result["agent_name"] = self.agent_name
        if self.tool_name:
            result["tool_name"] = self.tool_name
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary"""
        return cls(
            role=data["role"], 
            content=data["content"],
            agent_name=data.get("agent_name"),
            tool_name=data.get("tool_name")
        )
    
    def __repr__(self) -> str:
        if self.role == "tool_call":
            return f"Message(role='{self.role}', agent='{self.agent_name}', tool='{self.tool_name}', content='{self.content[:50]}...')"
        return f"Message(role='{self.role}', content='{self.content[:50]}...')"


class ResponseMessage:
    """Represents a single response message from an agent"""
    
    def __init__(self, role: str, content: str, agent_name: Optional[str] = None, tool_name: Optional[str] = None):
        self.role = role  # "assistant", "tool_call"
        self.content = content
        self.agent_name = agent_name  # For tool calls
        self.tool_name = tool_name    # For tool calls
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response message to dictionary format"""
        result = {"role": self.role, "content": self.content}
        if self.agent_name:
            result["agent_name"] = self.agent_name
        if self.tool_name:
            result["tool_name"] = self.tool_name
        return result


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
        return [message.to_dict() for message in self.conversation_history]

    async def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
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