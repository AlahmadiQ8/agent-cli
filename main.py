import argparse
import sys

from cli_chat_interface import CliChatInterface
from agents.mock_chatbot import MockChatbot


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Interactive AI Agent CLI for prototyping")
    parser.add_argument("--version", action="version", version="agent-cli 0.1.0")
    parser.add_argument("--agent", choices=["mock", "openai", "anthropic", "local"], 
                       default="mock", help="Agent type to use")
    parser.add_argument("--agent-name", type=str, help="Custom agent name")
    
    args = parser.parse_args()
    
    # Create agent based on type
    if args.agent == "mock":
        agent_name = args.agent_name or "MockBot"
        agent = MockChatbot(name=agent_name)
    # elif args.agent == "openai":
    #     agent = OpenAIAgent(name=args.agent_name or "OpenAI Assistant")
    # elif args.agent == "anthropic":
    #     agent = AnthropicAgent(name=args.agent_name or "Claude")
    # elif args.agent == "local":
    #     agent = LocalLLMAgent(name=args.agent_name or "Local LLM")
    else:
        agent = MockChatbot(name=args.agent_name or "MockBot")
    
    chat_interface = CliChatInterface(agent=agent)
    return chat_interface.run()


if __name__ == "__main__":
    sys.exit(main())
