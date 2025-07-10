# Agent CLI Chatbot 🤖

An interactive command-line chatbot for ai agent service (or any framework/platform).

## Features

- 💬 **Interactive chat interface** with markdown support
- 🎨 **Rich formatting** with bordered messages for clear role distinction
- 📝 **Command history** via agent threads (and also stores locally)

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

Start the chatbot with different agent types:

```bash
# Use Azure AI Agent Service (default)
python main.py --agent ai-agent

# Use mock agent for testing
python main.py --agent mock

# Custom agent name
python main.py --agent ai-agent --agent-name "MyCustomAgent"
```

### Agent Types

- **`ai-agent`**: Azure AI Agent Service with tool calling capabilities
- **`mock`**: Mock agent for testing and development

### Available Commands

- **Chat**: Simply type your message and press Enter
- **`exit`**: Quit the application
- **`clear`**: Clear the screen and show welcome message
- **`help`**: Show welcome message with commands
- **`history`**: Display recent chat history
- **`Ctrl+C`**: Exit the application

## Example Session

```bash
🤖 Agent CLI
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Welcome to Agent CLI Chatbot! 🚀                
│                                                                            
│ This is a prototype testing environment for AI agents with the following   
│ features:                                                                  
│                                                                            
│ • 💬 Interactive chat with markdown support                                
│ • 🎨 Rich formatting with bordered messages                                
│ • 📝 Command history (saved to .chat_history)                              
│ • 🔧 Azure AI integration with tool support                                
└─────────────────────────────────────────────────────────────────────────────────┘

💬 You: Can you help me create a Python file with a simple calculator?

┌─ 👤 User ────────────────────────────────────────────────────────────────────────┐
│                                                                               
│ Can you help me create a Python file with a simple calculator?                
│                                                                               
└──────────────────────────────────────────────────────────────────────────────────┘

┌─ 🔧 Tool Call ────────────────────────────────────────────────────────────────────┐
│                                                                              
│ create_file                                                                  
│ Creating calculator.py with basic arithmetic functions...                    
│                                                                              
└──────────────────────────────────────────────────────────────────────────────────┘

┌─ 🤖 Assistant ───────────────────────────────────────────────────────────────────┐
│                                                                                
│ I'll create a simple calculator Python file for you!                           
│                                                                                
│ **calculator.py** has been created with the following features:                
│                                                                                
│ • ➕ Addition                                                                  
│ • ➖ Subtraction                                                               
│ • ✖️ Multiplication                                                            
│ • ➗ Division (with zero-division handling)                                    
│ • 📱 Interactive menu system                                                   
│                                                                                
│ The calculator includes error handling and a user-friendly interface. You can  
│ run it with: `python calculator.py`                                            
│                                                                                
│ Would you like me to add any additional features like advanced operations?     
│                                                                                
└──────────────────────────────────────────────────────────────────────────────────┘
```
