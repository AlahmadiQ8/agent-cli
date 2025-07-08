# Agent CLI Chatbot 🤖

An interactive command-line chatbot built with Rich and prompt_toolkit for quickly prototyping and testing AI agents.

## Features

- 💬 **Interactive chat interface** with markdown support
- 🎨 **Rich formatting** with bordered messages for clear role distinction
- 📝 **Command history** (automatically saved to `.chat_history`)
- 🤖 **Mock responses** with realistic delays for testing
- 🎯 **Special commands** for enhanced functionality

## Installation

Make sure you have Python 3.11+ installed, then install dependencies:

```bash
pip install -r requirements.txt
```

Or if using uv:

```bash
uv sync
```

## Usage

Start the chatbot:

```bash
python main.py
```

### Available Commands

- **Chat**: Simply type your message and press Enter
- **`exit`**: Quit the application
- **`clear`**: Clear the screen and show welcome message
- **`help`**: Show welcome message with commands
- **`history`**: Display recent chat history
- **`Ctrl+C`**: Exit the application

## Example Session

```
🤖 Agent CLI
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               Welcome to Agent CLI Chatbot! 🚀                 │
│                                                                                │
│ This is a prototype testing environment for AI agents with the following       │
│ features:                                                                      │
│                                                                                │
│ • 💬 Interactive chat with markdown support                                   │
│ • 🎨 Rich formatting with bordered messages                                   │
│ • 📝 Command history (saved to .chat_history)                                │
│ • 🤖 Mock responses for quick testing                                         │
└─────────────────────────────────────────────────────────────────────────────────┘

💬 You: Hello, can you help me with Python?

┌─ 👤 User ─────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│   Hello, can you help me with Python?                                           │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘

┌─ 🤖 Assistant ────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│   That's an interesting question! Let me think about it...                      │
│                                                                                  │
│   Here are some key points to consider:                                         │
│                                                                                  │
│   1. First principle: Always start with the basics                              │
│   2. Second principle: Build incrementally                                       │
│   3. Third principle: Test early and often                                      │
│                                                                                  │
│   > "The best code is code that doesn't exist" - Unknown                       │
│                                                                                  │
│   Would you like me to elaborate on any of these points?                        │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

## Features in Detail

### Mock Response System

The chatbot includes a sophisticated mock response system that:

- Provides varied responses based on input length
- Includes realistic typing delays (0.5-2 seconds)
- Supports markdown formatting including:
  - **Bold** and *italic* text
  - Code blocks with syntax highlighting
  - Lists and numbered lists
  - Blockquotes
  - Headers

### Chat History

- Automatically saves command history to `.chat_history` file
- Use `history` command to view recent conversations
- Navigate through previous inputs using arrow keys

### Visual Design

- **User messages**: Blue bordered panels with 👤 icon
- **Assistant messages**: Green bordered panels with 🤖 icon
- **System messages**: Cyan bordered panels
- **Typing indicator**: Shows "Thinking..." while generating responses

## Development

This CLI is designed for rapid prototyping of AI agents. To customize:

1. **Modify responses**: Edit the `MockChatbot` class in `main.py`
2. **Add new commands**: Extend the `handle_command` method
3. **Change styling**: Modify the `display_message` method
4. **Add new features**: Extend the `ChatInterface` class

## Dependencies

- `rich`: For beautiful terminal formatting
- `prompt_toolkit`: For interactive prompts and history
- `click`: For command-line interface (optional)

## License

This project is open source and available under the MIT License.
