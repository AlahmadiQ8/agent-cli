"""
Azure AI Tools Management

Handles creation and management of Azure AI tools like Bing grounding.
"""
import logging
from typing import Optional

from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import AsyncToolSet, Tool, BingGroundingTool
from azure.ai.projects.models import ConnectionType

logger = logging.getLogger(__name__)


class AzureToolManager:
    """Manages Azure AI tools for agents"""

    def __init__(self, ai_client: AIProjectClient, language: str = "en-US"):
        self.ai_client = ai_client
        self.language = language

    async def find_bing_connection_id(self) -> Optional[str]:
        """Find Bing grounding connection ID"""
        try:
            conn_list = self.ai_client.connections.list()
            async for conn in conn_list:
                if (conn.type == ConnectionType.API_KEY and 
                    conn.metadata.get("type") == "bing_grounding"):
                    logger.info(f"Found Bing connection: {conn.id}")
                    return conn.id
            
            logger.info("No Bing grounding connection found")
            return None
            
        except Exception as e:
            logger.error(f"Error finding Bing connection: {e}")
            return None

    async def create_bing_tool(self) -> Optional[Tool]:
        """Create Bing grounding tool if connection exists"""
        conn_id = await self.find_bing_connection_id()
        if not conn_id:
            logger.warning("Bing grounding tool not found. Please create a connection with type 'bing_grounding'.")
            return None
        
        return BingGroundingTool(
            connection_id=conn_id,
            set_lang=self.language,
        )

    async def build_toolset(self) -> AsyncToolSet:
        """Build complete toolset for agent"""
        toolset = AsyncToolSet()
        
        # Add Bing tool if available
        bing_tool = await self.create_bing_tool()
        if bing_tool:
            toolset.add(bing_tool)
            logger.info("Added Bing grounding tool to agent")
        
        # Future: Add other tools here (file search, code interpreter, etc.)
        
        return toolset
