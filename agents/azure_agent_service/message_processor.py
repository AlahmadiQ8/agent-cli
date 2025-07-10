"""
Azure AI Message Processing

Handles processing of Azure AI agent responses and run steps.
"""
import logging
from typing import List, Optional

from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import (
    RunStepBingGroundingToolCall,
    RunStepMessageCreationReference,
    RunStepType,
    ListSortOrder
)

from agents.base_agent import ResponseMessage

logger = logging.getLogger(__name__)


class AzureMessageProcessor:
    """Processes Azure AI agent messages and run steps"""

    def __init__(self, ai_client: AIProjectClient, agent_name: str):
        self.ai_client = ai_client
        self.agent_name = agent_name

    def process_tool_call_step(self, step, step_details) -> Optional[ResponseMessage]:
        """Process tool call step and extract information"""
        try:
            tool_calls = step_details.get(RunStepType.TOOL_CALLS, [])
            for call in tool_calls:
                if isinstance(call, RunStepBingGroundingToolCall):
                    request_url = call.bing_grounding.get("requesturl", "No URL provided")
                    status = step.get('status', 'unknown')
                    
                    return ResponseMessage(
                        role="tool_call",
                        content=request_url,
                        agent_name=self.agent_name,
                        tool_name=f"{call.type} ({status})"
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing tool call step: {e}")
            return None

    async def process_message_creation_step(self, step_details, thread_id: str) -> Optional[ResponseMessage]:
        """Process message creation step and extract assistant response"""
        try:
            message_creation = step_details.get(RunStepType.MESSAGE_CREATION, {})
            if not isinstance(message_creation, RunStepMessageCreationReference):
                return None
            
            # Get the actual message
            message = await self.ai_client.agents.messages.get(
                thread_id=thread_id, 
                message_id=message_creation.message_id
            )
            
            # Extract text content
            text_contents = message.text_messages
            if not text_contents:
                return None
            
            # Build citations
            annotations_list = [
                f"- [{annotation.url_citation.title}]({annotation.url_citation.url})" 
                for annotation in message.url_citation_annotations
            ]
            
            # Combine message and citations
            final_message = text_contents[-1].text.value
            if annotations_list:
                annotations_str = "\n".join(annotations_list)
                final_message += f"\n\n**Citations:**\n{annotations_str}"
            
            return ResponseMessage(role="assistant", content=final_message)
            
        except Exception as e:
            logger.error(f"Error processing message creation step: {e}")
            return None

    async def process_run_steps(self, thread_id: str, run_id: str) -> List[ResponseMessage]:
        """Process all run steps and extract response messages"""
        try:
            run_steps = self.ai_client.agents.run_steps.list(
                thread_id=thread_id, 
                run_id=run_id, 
                order=ListSortOrder.ASCENDING
            )

            results = []
            steps = []
            
            # Collect all steps
            async for step in run_steps:
                steps.append(step)
            
            logger.debug(f"Processing {len(steps)} run steps")
            
            # Process each step
            for step in steps:
                step_details = step.get("step_details", {})
                
                if step.type == RunStepType.TOOL_CALLS:
                    tool_result = self.process_tool_call_step(step, step_details)
                    if tool_result:
                        results.append(tool_result)
                        
                elif step.type == RunStepType.MESSAGE_CREATION:
                    message_result = await self.process_message_creation_step(step_details, thread_id)
                    if message_result:
                        results.append(message_result)

            logger.info(f"Processed {len(results)} response messages")
            return results
            
        except Exception as e:
            logger.error(f"Error processing run steps: {e}")
            return []
