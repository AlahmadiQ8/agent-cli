from typing import Any, Dict, Optional
import os
import logging
import asyncio

from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import (
    Agent,
    AsyncToolSet,
    AzureAISearchTool,
    FilePurpose,
    FileSearchTool,
    Tool,
    MessageRole,
    BingGroundingTool
)
from azure.ai.projects.models import ConnectionType, ApiKeyCredentials
from azure.identity.aio import DefaultAzureCredential
from azure.core.credentials_async import AsyncTokenCredential

from agents.base_agent import BaseAgent

from dotenv import load_dotenv

from storage import TemporaryFileStorage

load_dotenv()

logger = logging.getLogger("aiAgentService")


class AzureAIAgentServiceAgent(BaseAgent):
    """AI Agent Service Agent for Azure AI Projects"""

    def __init__(self, name: str = "MyCoolAgent"):
        super().__init__(name)
        self.proj_endpoint = os.environ.get("AZURE_EXISTING_AIPROJECT_ENDPOINT")
        self.agent_id = os.environ.get("AZURE_AI_AGENT_ID")
        self.azure_agent: Optional[Agent] = None
        self.ai_client: Optional[AIProjectClient] = None
        self.creds: Optional[AsyncTokenCredential] = None
        self._initialized = False
        self.thread_id = None 
        self.storage = TemporaryFileStorage()

    async def _get_bing_tool_if_available(self) -> Tool | None:
        conn_list = self.ai_client.connections.list() # type: ignore
        conn_id = None
        async for conn in conn_list:
            if conn.type == ConnectionType.API_KEY and conn.metadata.get("type") == "bing_grounding":
                conn_id = conn.id
                break
        
        if conn_id:
            return BingGroundingTool(
                connection_id=conn_id,
                set_lang="en-US",   
            )
        else:
            logger.warning("Bing grounding tool not found. Please create a connection with type 'bing_grounding'.")
            return None

    async def _create_or_update_agent(self, agent: Agent | None, ai_client: AIProjectClient, creds: AsyncTokenCredential) -> Agent:
        """Create or update an Azure AI agent"""
        toolset = AsyncToolSet()
        bing_tool = await self._get_bing_tool_if_available()
        if bing_tool:
            toolset.add(bing_tool)
        
        instructions = "You are a helpful assistant. Use the tools provided to answer questions."
        
        if agent is None:
            logger.info("Creating new agent with resources")
            agent = await ai_client.agents.create_agent(
                model=os.environ["AZURE_AI_AGENT_DEPLOYMENT_NAME"],
                name=os.environ["AZURE_AI_AGENT_NAME"],
                instructions=instructions,
                toolset=toolset
            )
        else:
            logger.info("Updating existing agent with resources")
            agent.instructions = instructions
            agent = await ai_client.agents.update_agent(
                agent_id=agent.id,
                model=os.environ["AZURE_AI_AGENT_DEPLOYMENT_NAME"],
                name=os.environ["AZURE_AI_AGENT_NAME"],
                instructions=instructions,
                toolset=toolset
            )
        
        return agent

    async def _initialize_azure_agent(self) -> Agent:
        """Initialize the Azure AI agent"""
        if not self.proj_endpoint:
            raise RuntimeError("AZURE_EXISTING_AIPROJECT_ENDPOINT environment variable is not set")
        

        try: 
            async with DefaultAzureCredential(exclude_shared_token_cache_credential=True) as creds:
                async with AIProjectClient(credential=creds, endpoint=self.proj_endpoint) as ai_client:
                    if self.agent_id is not None: 
                        try:
                            agent = await ai_client.agents.get_agent(self.agent_id)
                            agent = await self._create_or_update_agent(agent, ai_client, creds)
                            logger.info(f"Found agent by ID: {agent.id}. Updating agent")
                            self.name = agent.name
                            return agent
                        except Exception as e:
                            logger.warning(f"Could not retrieve agent by AZURE_AGENT_ID = \"{self.agent_id}\". Will create a new agent.")
                    
                    agent_list = ai_client.agents.list_agents()
                    if agent_list:
                        async for agent_object in agent_list:
                            if agent_object.name == os.environ["AZURE_AI_AGENT_NAME"]:
                                logger.info(f"Found existing agent named '{agent_object.name}', ID: {agent_object.id}")
                                os.environ["AZURE_AI_AGENT_ID"] = agent_object.id
                                self.agent_id = agent_object.id
                                agent = await ai_client.agents.get_agent(self.agent_id)
                                agent = await self._create_or_update_agent(agent, ai_client, creds)
                                self.name = agent.name
                                return agent
                    
                    # Create a new agent
                    agent = await self._create_or_update_agent(None, ai_client, creds)
                    os.environ["AZURE_AI_AGENT_ID"] = agent.id
                    self.agent_id = agent.id
                    logger.info(f"Created agent, agent ID: {agent.id}")

                    self.name = agent.name
                    return agent
        except Exception as e:
            logger.error(f"Error creating agent: {e}", exc_info=True)
            raise RuntimeError(f"Failed to create the agent: {e}")

    async def _initialize_thread(self):
        thread_id = self.storage.retrieve("thread_id")
        if (not thread_id) or (thread_id is None):
            self.thread = await self.ai_client.agents.threads.create() # type: ignore
            self.storage.store("thread_id", self.thread.id)
        else:
            self.thread = await self.ai_client.agents.threads.get(thread_id) # type: ignore

    async def initialize(self) -> bool:
        """Async version of initialize for use in async contexts"""
        try:
            if not self.proj_endpoint:
                raise RuntimeError("AZURE_EXISTING_AIPROJECT_ENDPOINT environment variable is not set")
            
            self.creds = DefaultAzureCredential()
            self.ai_client = AIProjectClient(credential=self.creds, endpoint=self.proj_endpoint)
            self.azure_agent = await self._initialize_azure_agent()
            await self._initialize_thread()
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI agent: {e}")
            return False
    
    async def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history"""

        await super().add_user_message(content)

        if self.thread is None:
            self.thread = await self.ai_client.agents.threads.create() # type: ignore
            self.storage.store("thread_id", self.thread.id)

        message = await self.ai_client.agents.messages.create( # type: ignore
                thread_id=self.thread.id,
                content=content,
                role=MessageRole.USER,
            )
        logger.info(f"User message sent: {message.id}")

    async def generate_response(self) -> str:
        """Generate response using Azure AI agent"""
        if not self._initialized or self.azure_agent is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        try:
            run = await self.ai_client.agents.runs.create_and_process( # type: ignore
                thread_id=self.thread.id, # type: ignore
                agent_id=self.azure_agent.id,
            )
            logger.info(f"Run started with ID: {run.id}")

            if run.status == "failed":
                logger.error(f"Run failed: {run.last_error}")
            
            result = await self.ai_client.agents.messages.get_last_message_text_by_role(thread_id=self.thread.id, role=MessageRole.AGENT) # type: ignore

            if (result is None):
                raise RuntimeError("No response received from Azure AI agent.")
            
            return result.text.value
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_response = f"Error generating response: {e}"
            return error_response

    async def get_status(self) -> Dict[str, Any]:
        """Get Azure AI agent status"""
        return {
            "name": self.name,
            "type": "azure_ai_agent_service",
            "initialized": self._initialized,
            "conversation_length": await self.get_conversation_length(),
            "azure_agent_id": self.agent_id,
            "azure_agent_name": self.azure_agent.name if self.azure_agent else None,
            "project_endpoint": self.proj_endpoint,
        }

    async def clear_conversation_history(self) -> None:
        await super().clear_conversation_history()
        await self.ai_client.agents.threads.delete(self.thread.id)  # type: ignore
        self.storage.delete("thread_id")
        self.thread = None