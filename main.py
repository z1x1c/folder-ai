import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
import ollama

# Initialize the rich console
console = Console()

class AIAgent:
    def __init__(self):
        self.model = "qwen2.5"  # default model
        
    def get_directory_info(self):
        """Get information about the current directory"""
        try:
            # Get list of files and directories
            items = os.listdir('.')
            files = [f for f in items if os.path.isfile(f)]
            dirs = [d for d in items if os.path.isdir(d)]
            
            # Create a summary of the directory
            summary = f"Directory contains {len(files)} files and {len(dirs)} directories.\n"
            summary += f"Files: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}\n"
            summary += f"Directories: {', '.join(dirs[:5])}{'...' if len(dirs) > 5 else ''}"
            return summary
        except Exception as e:
            return f"Error reading directory: {str(e)}"

    def answer_query(self, query):
        """Answer a query about the current directory"""
        try:
            # Get directory information
            dir_info = self.get_directory_info()
            
            # Create prompt for the AI
            prompt = f"""Based on this directory information:
            {dir_info}

            Answer this question: {query}

            Please provide a concise and relevant answer."""

            # Get streaming response from ollama
            stream = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                stream=True
            )
            
            # Initialize response content
            content = ""
            
            # Create a live display
            with Live(Panel(content, title=self.summarize_query(query), expand=False), refresh_per_second=10) as live:
                for chunk in stream:
                    if 'message' in chunk:
                        content += chunk['message'].get('content', '')
                        live.update(Panel(content, title=self.summarize_query(query), expand=False))
            
            return content
        except Exception as e:
            return f"Error processing query: {str(e)}"

    def summarize_query(self, query):
        """Create a title from the query"""
        # Remove question marks and capitalize first letter
        title = query.rstrip('?').capitalize()
        # Truncate if too long
        return (title[:50] + '...') if len(title) > 50 else title


def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/] python main.py '<query>'")
        sys.exit(1)

    query = sys.argv[1]
    agent = AIAgent()
    
    # Get the answer (now with streaming)
    answer = agent.answer_query(query)


if __name__ == "__main__":
    main()
