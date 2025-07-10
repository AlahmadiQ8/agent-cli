"""
Azure AI Agent Configuration

Centralizes configuration management for Azure AI Agent Service.
"""
import os
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class AzureConfig:
    """Configuration for Azure AI Agent Service"""
    project_endpoint: str
    deployment_name: str
    agent_name: str
    agent_id: Optional[str] = None
    language: str = "en-US"
    instructions: str = "You are a helpful assistant. Use the tools provided to answer questions."

    @classmethod
    def from_environment(cls) -> 'AzureConfig':
        """Load configuration from environment variables"""
        missing_vars = []
        
        # Check required environment variables
        project_endpoint = os.environ.get("AZURE_EXISTING_AIPROJECT_ENDPOINT")
        deployment_name = os.environ.get("AZURE_AI_AGENT_DEPLOYMENT_NAME")
        agent_name = os.environ.get("AZURE_AI_AGENT_NAME")
        
        if not project_endpoint:
            missing_vars.append("AZURE_EXISTING_AIPROJECT_ENDPOINT")
        if not deployment_name:
            missing_vars.append("AZURE_AI_AGENT_DEPLOYMENT_NAME")
        if not agent_name:
            missing_vars.append("AZURE_AI_AGENT_NAME")
            
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Type assertion since we've validated they exist
        assert project_endpoint is not None
        assert deployment_name is not None
        assert agent_name is not None
        
        return cls(
            project_endpoint=project_endpoint,
            deployment_name=deployment_name,
            agent_name=agent_name,
            agent_id=os.environ.get("AZURE_AI_AGENT_ID"),
            language=os.environ.get("AZURE_AI_BING_LANGUAGE", "en-US")
        )

    def validate(self) -> None:
        """Validate configuration"""
        if not self.project_endpoint.startswith(("https://", "http://")):
            raise ValueError("Project endpoint must be a valid URL")
        if not self.deployment_name:
            raise ValueError("Deployment name cannot be empty")
        if not self.agent_name:
            raise ValueError("Agent name cannot be empty")
        
        logger.info(f"Configuration validated for agent: {self.agent_name}")
