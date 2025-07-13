import argparse
import sys

from agents import AzureAIAgentServiceAgent, MockChatbot
from cli_chat_interface import CliChatInterface

import asyncio

def main():
    """Main entry point"""
    
    async def async_main():
        parser = argparse.ArgumentParser(description="Interactive AI Agent CLI for prototyping")
        parser.add_argument("--version", action="version", version="agent-cli 0.1.0")
        parser.add_argument("--agent", choices=["mock", "openai", "ai-agent"], 
                           default="mock", help="Agent type to use")
        parser.add_argument("--agent-name", type=str, help="Custom agent name")
        
        args = parser.parse_args()
        
        # Create agent based on type
        if args.agent == "mock":
            agent_name = args.agent_name or "MockBot"
            agent = MockChatbot(name=agent_name)
        # elif args.agent == "openai":
        #     agent = OpenAIAgent(name=args.agent_name or "OpenAI Assistant")
        elif args.agent == "ai-agent":
            agent = AzureAIAgentServiceAgent()
        else:
            agent = MockChatbot(name=args.agent_name or "MockBot")
        
        # Use async context manager for proper resource cleanup
        async with agent:
            chat_interface = CliChatInterface(agent=agent)
            
            # Run the async chat interface
            return await chat_interface.run()
    
    # Run everything async
    try:
        return asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Thanks for testing the Agent CLI!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
