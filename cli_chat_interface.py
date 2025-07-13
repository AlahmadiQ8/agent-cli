from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from agents.base_agent import BaseAgent
from agents.mock_chatbot import MockChatbot

class CliChatInterface:
    """Rich-based chat interface with bordered messages"""

    def __init__(self, agent: Optional[BaseAgent] = None):
        self.console = Console()
        self.agent = agent or MockChatbot()

    def display_message(self, role: str, message: str, agent_name: Optional[str] = None, tool_name: Optional[str] = None):
        """Display a message with role-specific styling"""
        if role == "user":
            title = "👤 User"
            border_style = "blue"
            title_style = "bold blue"
        elif role == "tool_call":
            title = f"🔧 {agent_name} → {tool_name}"
            border_style = "yellow"
            title_style = "bold yellow"
        else:  # assistant
            title = f"🤖 {self.agent.name}"
            border_style = "green"
            title_style = "bold green"

        # Render markdown content
        content = Markdown(message)

        panel = Panel(
            content,
            title=title,
            title_align="left",
            border_style=border_style,
            padding=(1, 2),
            expand=False
        )

        self.console.print(panel)
        self.console.print()  # Add spacing



    def display_welcome(self):
        """Display welcome message"""
        welcome_text = f"""
# Welcome to Agent CLI Chatbot! 🚀

Currently using: **{self.agent.name}**

This is a **prototype testing environment** for AI agents with the following features:

- 💬 **Interactive chat** with markdown support
- 🎨 **Rich formatting** with bordered messages  
- 📝 **Command history** (saved to `.chat_history`)
- 🤖 **Pluggable agents** for easy testing

## Commands:
- Type your message and press **Enter** to chat
- Use **Ctrl+C** or type `exit` to quit
- Type `clear` to clear the screen
- Type `help` for this message
- Type `history` to see recent chat history
- Type `status` to see agent information

---
*Start chatting below!*
        """

        panel = Panel(
            Markdown(welcome_text),
            title="🤖 Agent CLI",
            title_align="center",
            border_style="cyan",
            padding=(1, 2)
        )

        self.console.print(panel)
        self.console.print()

    async def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = user_input.strip().lower()

        if command == "exit":
            self.console.print("👋 Goodbye! Thanks for testing the Agent CLI!", style="bold cyan")
            return True

        elif command == "clear":
            self.console.clear()
            await self.agent.clear_conversation_history()
            self.display_welcome()
            return True

        elif command == "help":
            self.display_welcome()
            return True

        elif command == "history":
            await self.display_chat_history()
            return True

        elif command == "status":
            await self.display_agent_status()
            return True

        return False

    async def display_chat_history(self):
        """Display chat history summary"""
        conversation_history = await self.agent.get_conversation_history()
        if not conversation_history:
            self.console.print("No chat history yet.", style="dim")
            return

        history_text = f"## Chat History ({len(conversation_history)} messages)\n\n"
        for i, message_dict in enumerate(conversation_history[-5:], 1):  # Show last 5
            role = message_dict["role"]
            content = message_dict["content"]
            preview = content[:100] + "..." if len(content) > 100 else content
            history_text += f"{i}. **{role.title()}**: {preview}\n"

        panel = Panel(
            Markdown(history_text),
            title="📚 History",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()

    async def display_agent_status(self):
        """Display agent status and information"""
        status = await self.agent.get_status()

        status_text = "## Agent Status\n\n"
        status_text += f"**Name**: {status.get('name', 'Unknown')}\n"
        status_text += f"**Type**: {status.get('type', 'Unknown')}\n"
        status_text += f"**Initialized**: {status.get('initialized', False)}\n"
        status_text += f"**Conversation Length**: {status.get('conversation_length', 0)} messages\n\n"

        capabilities = status.get('capabilities', {})
        if capabilities:
            status_text += "### Capabilities\n"
            for key, value in capabilities.items():
                status_text += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        panel = Panel(
            Markdown(status_text),
            title="📊 Agent Status",
            border_style="magenta",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()

    async def run(self):
        """Main chat loop"""
        try:
            # Setup prompt session with history
            session = PromptSession(
                history=FileHistory('storage/.chat_history'),
                multiline=False,
            )

            self.console.clear()
            self.display_welcome()

            while True:
                try:
                    # Get user input (async)
                    user_input = await session.prompt_async("💬 You: ")

                    if not user_input.strip():
                        continue

                    # Clear screen and redisplay welcome for clean interface
                    self.console.clear()
                    self.display_welcome()

                    # Redisplay recent chat history
                    recent_messages = await self.agent.get_recent_messages(6)  # Show last 6 messages
                    for message_dict in recent_messages:
                        self.display_message(
                            message_dict["role"], 
                            message_dict["content"],
                            message_dict.get("agent_name"),
                            message_dict.get("tool_name")
                        )

                    # Handle special commands
                    if await self.handle_command(user_input):
                        if user_input.strip().lower() == "exit":
                            break
                        continue

                    # Display user message
                    self.display_message("user", user_input)

                    # Add user message to agent's conversation history
                    await self.agent.add_user_message(user_input)

                    # Get bot response (async) - now returns a list of ResponseMessage objects
                    response_messages = await self.agent.generate_response(user_input)

                    # Display and store each response message
                    for response_msg in response_messages:
                        # Display the message with appropriate styling
                        self.display_message(
                            response_msg.role, 
                            response_msg.content,
                            response_msg.agent_name,
                            response_msg.tool_name
                        )
                        
                        # Add to conversation history
                        if response_msg.role == "tool_call":
                            await self.agent.add_tool_call_message(
                                response_msg.content,
                                response_msg.agent_name or "Unknown",
                                response_msg.tool_name or "Unknown"
                            )
                        else:  # assistant message
                            await self.agent.add_assistant_message(response_msg.content)

                except KeyboardInterrupt:
                    self.console.print("\n👋 Goodbye! Thanks for testing the Agent CLI!", style="bold cyan")
                    break
                except EOFError:
                    break

        except Exception as e:
            self.console.print(f"❌ Error: {e}", style="bold red")
            return 1

        return 0