"""
Azure AI Agent Service Agent

Simplified and organized Azure AI Projects integration with proper separation of concerns.
"""
from typing import Any, Dict, Optional, List
import os
import logging

from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import Agent, MessageRole, ListSortOrder
from azure.identity.aio import DefaultAzureCredential

from agents.base_agent import BaseAgent, ResponseMessage
from .config import AzureConfig
from .tools import AzureToolManager
from .message_processor import AzureMessageProcessor
from storage import TemporaryFileStorage

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AzureAIAgentServiceAgent(BaseAgent):
    """
    Simplified Azure AI Agent Service Agent
    
    Integrates with Azure AI Projects using proper separation of concerns.
    """

    def __init__(self, name: str = "AzureAIAgent"):
        super().__init__(name)

        self.conversation_history: List[ResponseMessage] = []
        
        # Load and validate configuration
        self.config = AzureConfig.from_environment()
        self.config.validate()
        
        # Azure resources
        self.azure_agent: Optional[Agent] = None
        self.ai_client: Optional[AIProjectClient] = None
        self.thread = None
        
        # Helper components
        self.tool_manager: Optional[AzureToolManager] = None
        self.message_processor: Optional[AzureMessageProcessor] = None
        
        # State
        self._initialized = False
        self.storage = TemporaryFileStorage()

    async def _create_or_update_agent(self, existing_agent: Optional[Agent] = None) -> Agent:
        """Create or update Azure AI agent with tools"""
        if not self.ai_client or not self.tool_manager:
            raise RuntimeError("AI client or tool manager not initialized")
        
        toolset = await self.tool_manager.build_toolset()
        
        if existing_agent is None:
            logger.info("Creating new Azure AI agent")
            agent = await self.ai_client.agents.create_agent(
                model=self.config.deployment_name,
                name=self.config.agent_name,
                instructions=self.config.instructions,
                toolset=toolset
            )
        else:
            logger.info(f"Updating existing agent: {existing_agent.id}")
            agent = await self.ai_client.agents.update_agent(
                agent_id=existing_agent.id,
                model=self.config.deployment_name,
                name=self.config.agent_name,
                instructions=self.config.instructions,
                toolset=toolset
            )
        
        logger.info(f"Agent configured: {agent.id}")
        return agent

    async def _find_existing_agent(self) -> Optional[Agent]:
        """Find existing agent by ID or name"""
        if not self.ai_client:
            return None
        
        # Try to find by ID first
        if self.config.agent_id:
            try:
                agent = await self.ai_client.agents.get_agent(self.config.agent_id)
                logger.info(f"Found agent by ID: {agent.id}")
                self.name = agent.name
                return agent
            except Exception as e:
                logger.warning(f"Could not retrieve agent by ID '{self.config.agent_id}': {e}")
        
        # Try to find by name
        try:
            agent_list = self.ai_client.agents.list_agents()
            async for agent_object in agent_list:
                if agent_object.name == self.config.agent_name:
                    logger.info(f"Found agent by name '{agent_object.name}': {agent_object.id}")
                    # Update configuration
                    os.environ["AZURE_AI_AGENT_ID"] = agent_object.id
                    self.config.agent_id = agent_object.id
                    self.name = agent_object.name
                    return await self.ai_client.agents.get_agent(agent_object.id)
        except Exception as e:
            logger.warning(f"Error searching for agent by name: {e}")
        
        return None

    async def _initialize_azure_resources(self) -> None:
        """Initialize Azure AI client and agent"""
        # Initialize credentials and client
        self.credentials = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        self.ai_client = AIProjectClient(
            credential=self.credentials, 
            endpoint=self.config.project_endpoint
        )
        
        # Initialize helper components
        self.tool_manager = AzureToolManager(self.ai_client, self.config.language)
        self.message_processor = AzureMessageProcessor(self.ai_client, self.name)
        
        # Find or create agent
        existing_agent = await self._find_existing_agent()
        self.azure_agent = await self._create_or_update_agent(existing_agent)
        
        # Update configuration if new agent was created
        if not self.config.agent_id:
            os.environ["AZURE_AI_AGENT_ID"] = self.azure_agent.id
            self.config.agent_id = self.azure_agent.id
        
        self.name = self.azure_agent.name

    async def _initialize_thread(self) -> None:
        """Initialize or retrieve conversation thread"""
        if not self.ai_client:
            raise RuntimeError("AI client not initialized")
        
        thread_id = self.storage.retrieve("thread_id")
        
        try:
            if thread_id:
                self.thread = await self.ai_client.agents.threads.get(thread_id)
                logger.info(f"Retrieved existing thread: {thread_id}")
            else:
                self.thread = await self.ai_client.agents.threads.create()
                self.storage.store("thread_id", self.thread.id)
                logger.info(f"Created new thread: {self.thread.id}")
        except Exception as e:
            logger.warning(f"Error with thread {thread_id}, creating new one: {e}")
            self.thread = await self.ai_client.agents.threads.create()
            self.storage.store("thread_id", self.thread.id)

    async def initialize(self) -> bool:
        """Initialize the Azure AI agent and all resources"""
        try:
            logger.info("Initializing Azure AI Agent Service...")
            
            await self._initialize_azure_resources()
            await self._initialize_thread()
            self.conversation_history = await self.get_conversation_history()
            
            self._initialized = True
            logger.info(f"Azure AI Agent '{self.name}' initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI agent: {e}")
            self._initialized = False
            return False

    async def add_user_message(self, content: str) -> None:
        """Add user message to conversation"""
        if not self._initialized:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        # Ensure thread exists
        if self.thread is None:
            await self._initialize_thread()

        # Send to Azure
        if not self.ai_client or not self.thread:
            raise RuntimeError("AI client or thread not available")
        
        message = await self.ai_client.agents.messages.create(
            thread_id=self.thread.id,
            content=content,
            role=MessageRole.USER,
        )
        logger.info(f"User message sent: {message.id}")

        self.conversation_history.append(
            ResponseMessage(
                role="user",
                content=content,
                agent_name=self.name
            )
        )

    async def get_conversation_history(self, limit = -1) -> List[ResponseMessage]:
        """Get conversation history as list of dictionaries"""
        if not self.ai_client or not self.thread or not self.message_processor:
            raise RuntimeError("Required components not available")
        
        result: List[ResponseMessage] = []
        async for run in self.ai_client.agents.runs.list(
            thread_id=self.thread.id,
            order= ListSortOrder.ASCENDING
        ):  
            if run.status == "failed":
                error_msg = f"Azure AI run failed: {getattr(run, 'last_error', 'Unknown error')}"
                result.append(ResponseMessage(role="assistant", content=f"I encountered an error: {error_msg}"))
            
            stepMessages = await self.message_processor.process_run_steps(self.thread.id, run.id)
            result = result + stepMessages
        
        self.conversation_history = result
        if limit > 0:
            result = result[-limit:]
        return result

    async def get_recent_messages(self, count: int = 10) -> List[ResponseMessage]:
        """Get the most recent messages from conversation history"""
        return self.conversation_history[-count:] if count > 0 else self.conversation_history
    
    async def get_conversation_length(self) -> int:
        """Get the number of messages in conversation history"""
        return len(self.conversation_history)

    async def generate_response(self, user_input: str) -> List[ResponseMessage]:
        """Generate response using Azure AI agent"""
        if not self._initialized or not self.azure_agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        if not self.ai_client or not self.thread or not self.message_processor:
            raise RuntimeError("Required components not available")

        try:
            # Create and process run
            run = await self.ai_client.agents.runs.create_and_process(
                thread_id=self.thread.id,
                agent_id=self.azure_agent.id,
            )
            logger.info(f"Run completed with status: {run.status} (ID: {run.id})")

            # Handle failed runs
            if run.status == "failed":
                error_msg = f"Azure AI run failed: {getattr(run, 'last_error', 'Unknown error')}"
                logger.error(error_msg)
                return [ResponseMessage(role="assistant", content=f"I encountered an error: {error_msg}")]
            
            # Process run steps
            results = await self.message_processor.process_run_steps(self.thread.id, run.id)
            
            # Ensure we have a response
            if not results:
                fallback = "I wasn't able to generate a response. Please try rephrasing your question."
                return [ResponseMessage(role="assistant", content=fallback)]
            
            # Update conversation history
            self.conversation_history.extend(results)
            return results
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            logger.error(error_msg)
            return [ResponseMessage(role="assistant", content=f"I encountered an error: {str(e)}")]

    async def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "name": self.name,
            "type": "azure_ai_agent_service",
            "initialized": self._initialized,
            "conversation_length": await self.get_conversation_length(),
            "azure_agent_id": self.config.agent_id,
            "azure_agent_name": self.azure_agent.name if self.azure_agent else None,
            "project_endpoint": self.config.project_endpoint,
            "thread_id": self.thread.id if self.thread else None,
        }

    async def clear_conversation_history(self) -> None:
        """Clear conversation history and reset thread"""
        try:
            # Delete Azure thread
            if self.thread and self.ai_client:
                await self.ai_client.agents.threads.delete(self.thread.id)
                logger.info(f"Deleted Azure thread: {self.thread.id}")
            
            # Reset thread state
            self.storage.delete("thread_id")
            self.thread = None
            
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")
            # Reset local state even if Azure cleanup fails
            self.storage.delete("thread_id")
            self.thread = None

    async def close(self) -> None:
        """Close Azure AI client and clean up resources"""
        try:
            if self.ai_client:
                await self.ai_client.close()
                await self.credentials.close()
                logger.info("Azure AI client closed")
                self.ai_client = None
            
            # Reset state
            self._initialized = False
            
        except Exception as e:
            logger.error(f"Error closing Azure AI client: {e}")
