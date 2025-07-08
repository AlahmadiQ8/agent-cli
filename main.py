import argparse
import os
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.key_binding import KeyBindings

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.layout import Layout
from rich.align import Align

from mock_chatbot import MockChatbot


class ChatInterface:
    """Rich-based chat interface with bordered messages"""
    
    def __init__(self):
        self.console = Console()
        self.chatbot = MockChatbot()
        self.chat_history = []
        
    def display_message(self, role: str, message: str):
        """Display a message with role-specific styling"""
        if role == "user":
            title = "👤 User"
            border_style = "blue"
            title_style = "bold blue"
        else:
            title = "🤖 Assistant"
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
        welcome_text = """
# Welcome to Agent CLI Chatbot! 🚀

This is a **prototype testing environment** for AI agents with the following features:

- 💬 **Interactive chat** with markdown support
- 🎨 **Rich formatting** with bordered messages  
- 📝 **Command history** (saved to `.chat_history`)
- 🤖 **Mock responses** for quick testing

## Commands:
- Type your message and press **Enter** to chat
- Use **Ctrl+C** or type `exit` to quit
- Type `clear` to clear the screen
- Type `help` for this message

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
        
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = user_input.strip().lower()
        
        if command == "exit":
            self.console.print("👋 Goodbye! Thanks for testing the Agent CLI!", style="bold cyan")
            return True
            
        elif command == "clear":
            self.console.clear()
            self.display_welcome()
            return True
            
        elif command == "help":
            self.display_welcome()
            return True
            
        elif command == "history":
            self.display_chat_history()
            return True
            
        return False
        
    def display_chat_history(self):
        """Display chat history summary"""
        if not self.chat_history:
            self.console.print("No chat history yet.", style="dim")
            return
            
        history_text = f"## Chat History ({len(self.chat_history)} messages)\n\n"
        for i, (role, message) in enumerate(self.chat_history[-5:], 1):  # Show last 5
            preview = message[:100] + "..." if len(message) > 100 else message
            history_text += f"{i}. **{role.title()}**: {preview}\n"
            
        panel = Panel(
            Markdown(history_text),
            title="📚 History",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
        
    def run(self):
        """Main chat loop"""
        try:
            # Setup prompt session with history
            session = PromptSession(
                history=FileHistory('.chat_history'),
                multiline=False,
            )
            
            self.console.clear()
            self.display_welcome()
            
            while True:
                try:
                    # Get user input
                    user_input = session.prompt("💬 You: ")
                    
                    if not user_input.strip():
                        continue
                        
                    # Clear screen and redisplay welcome for clean interface
                    self.console.clear()
                    self.display_welcome()
                    
                    # Redisplay recent chat history
                    for role, message in self.chat_history[-6:]:  # Show last 6 messages
                        self.display_message(role, message)
                        
                    # Handle special commands
                    if self.handle_command(user_input):
                        if user_input.strip().lower() == "exit":
                            break
                        continue
                    
                    # Display user message
                    self.display_message("user", user_input)
                    
                    # Get bot response
                    bot_response = self.chatbot.get_response(user_input)
                    
                    # Display assistant response
                    self.display_message("assistant", bot_response)
                    
                    # Store in history
                    self.chat_history.append(("user", user_input))
                    self.chat_history.append(("assistant", bot_response))
                    
                except KeyboardInterrupt:
                    self.console.print("\n👋 Goodbye! Thanks for testing the Agent CLI!", style="bold cyan")
                    break
                except EOFError:
                    break
                    
        except Exception as e:
            self.console.print(f"❌ Error: {e}", style="bold red")
            return 1
            
        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Interactive AI Agent CLI for prototyping")
    parser.add_argument("--version", action="version", version="agent-cli 0.1.0")
    
    args = parser.parse_args()
    
    chat_interface = ChatInterface()
    return chat_interface.run()


if __name__ == "__main__":
    sys.exit(main())
