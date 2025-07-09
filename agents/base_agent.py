from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """Abstract base class for AI agents"""

    def __init__(self, name: str = "Agent", config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.conversation_history = []

    @abstractmethod
    def generate_response(self, user_input: str) -> str:
        """Generate a response to user input"""
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the agent (e.g., load model, connect to API)"""
        pass

    @abstractmethod
    def reset_conversation(self) -> None:
        """Reset the conversation history"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metadata"""
        pass

    @abstractmethod
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update agent configuration"""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and features"""
        pass