import random
import asyncio
from typing import Optional, Dict, Any, List

from agents.base_agent import BaseAgent, ResponseMessage


class MockChatbot(BaseAgent):
    """Mock chatbot with predefined responses for testing"""

    def __init__(self, name: str = "MockBot"):
        super().__init__(name)
        self.responses = [
            "That's an interesting question! Let me think about it...",
            "I understand what you're asking. Here's my take on it:",
            "Great point! From my perspective, I would say:",
            "That's a complex topic. Let me break it down for you:",
            "I've been thinking about this lately, and here's what I think:",
            "That reminds me of something important:",
            "Excellent question! The answer depends on several factors:",
            "I can help you with that. Here's what you need to know:",
            "That's a fascinating topic! Let me explain:",
            "I see what you mean. Here's how I would approach it:",
        ]

        self.detailed_responses = [
            """Here are some **key points** to consider:

1. **First principle**: Always start with the basics
2. **Second principle**: Build incrementally
3. **Third principle**: Test early and often

> "The best code is code that doesn't exist" - Unknown

Would you like me to elaborate on any of these points?""",

            """This is a multi-step process:

## Step 1: Planning
- Define your requirements
- Sketch out the architecture
- Consider edge cases

## Step 2: Implementation
```python
def example_function():
    return "Hello, World!"
```

## Step 3: Testing
Make sure to test thoroughly!""",

            """Let me share some insights:

- **Pros**: This approach has several advantages
- **Cons**: However, there are some drawbacks to consider
- **Alternatives**: You might also consider these options

The key is to find the right balance for your specific use case.""",

            """Here's what I recommend:

1. Start with a **simple prototype**
2. Gather **user feedback** early
3. Iterate based on **real data**

*Remember*: Perfect is the enemy of good!""",

            """That's a great question! Here's my analysis:

### Technical Considerations
- Performance implications
- Scalability concerns
- Maintenance overhead

### Business Considerations
- Cost-benefit analysis
- Time to market
- Resource allocation

What aspect would you like to explore further?"""
        ]

    async def generate_response(self, user_input: str) -> List[ResponseMessage]:
        """Generate a mock response with simulated thinking time"""
        await asyncio.sleep(random.uniform(0.1, 0.3))  # Simulate processing time (faster for testing)

        intro = random.choice(self.responses)
        detail = random.choice(self.detailed_responses)
        response_content = f"{intro}\n\n{detail}"
        
        # Create response messages - can include tool calls and assistant responses
        messages = []
        
        # Sometimes simulate a tool call
        if random.random() < 0.3:  # 30% chance of tool call
            tool_calls = [
                ("search_knowledge", "Searching knowledge base for relevant information..."),
                ("analyze_data", "Analyzing data patterns and trends..."),
                ("generate_code", "Generating code examples..."),
                ("format_response", "Formatting response with markdown..."),
                ("validate_logic", "Validating logical consistency...")
            ]
            tool_name, tool_content = random.choice(tool_calls)
            messages.append(ResponseMessage(
                role="tool_call",
                content=tool_content,
                agent_name=self.name,
                tool_name=tool_name
            ))
        
        # Always include the main assistant response
        messages.append(ResponseMessage(
            role="assistant",
            content=response_content
        ))
        
        return messages
    
    async def initialize(self) -> bool:
        """Initialize the mock agent"""
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metadata"""
        return {
            "name": self.name,
            "type": "mock",
            "initialized": True,
            "conversation_length": await self.get_conversation_length(),
        }