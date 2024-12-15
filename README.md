# folder-ai

A Python-based AI assistant that helps you understand and navigate your directory contents using natural language queries. The assistant uses the Qwen 2.5 model through Ollama to provide intelligent responses about files and directories in your current working directory.

## Features

- Directory analysis and summarization
- Natural language queries about directory contents
- Rich console output for better readability
- Powered by Ollama

## Prerequisites

- Python 3.x
- Ollama installed with your desired model

## Dependencies

- rich
- ollama

## Installation

1. Clone this repository
2. Create and activate a virtual environment (recommended)
3. Install the required dependencies:
   ```bash
   pip install rich ollama
   ```
4. Ensure Ollama is installed your model is available

## Usage

1. Start the Ollama service:
   ```bash
   ollama serve
   ```

2. Run the script with your query:
   ```bash
   python main.py "What files are in this directory?"
   ```

Example queries:
- "How many Python files are there?"
- "List all directories"
- "What's the largest file in this folder?"
- "Show me any configuration files"

The assistant will analyze your current directory and provide detailed responses to your queries about its contents.

## License

This project is open source and available under the MIT License.
