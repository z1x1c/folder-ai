import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.spinner import Spinner
import ollama
import mimetypes

# Initialize the rich console
console = Console()

class AIAgent:
    def __init__(self):
        self.model = "qwen2.5"  # default model
        self.max_file_size = 1024 * 1024  # 1MB limit for file reading
        self.text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.ini', '.conf'}
        
    def is_text_file(self, filepath):
        """Check if a file is a text file based on extension and content"""
        ext = os.path.splitext(filepath)[1].lower()
        if ext in self.text_extensions:
            return True
        mime_type, _ = mimetypes.guess_type(filepath)
        return mime_type and mime_type.startswith('text/')
        
    def get_directory_info(self):
        """Get information about the current directory including file contents"""
        try:
            summary = []
            total_files = 0
            total_dirs = 0
            
            # First, gather structure information
            for root, dirs, files in os.walk('.'):
                # Skip dotfolders
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                rel_path = os.path.relpath(root, '.')
                if rel_path == '.':
                    rel_path = 'current directory'
                    
                total_dirs += len(dirs)
                total_files += len(files)
                
                summary.append(f"\n### {rel_path}")
                
                # List directories
                if dirs:
                    summary.append("\nDirectories:")
                    for d in dirs:
                        summary.append(f"- {d}/")
                
                # List and process files
                if files:
                    summary.append("\nFiles:")
                    for f in files:
                        if f.startswith('.'):
                            summary.append(f"- {f} (dotfile)")
                            continue
                            
                        filepath = os.path.join(root, f)
                        try:
                            size = os.path.getsize(filepath)
                            size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
                            
                            if size <= self.max_file_size and self.is_text_file(filepath):
                                with open(filepath, 'r', encoding='utf-8') as file:
                                    content = file.read()
                                    summary.append(f"- {f} ({size_str})")
                                    summary.append(f"```\n{content[:1000]}{'...' if len(content) > 1000 else ''}\n```")
                            else:
                                summary.append(f"- {f} ({size_str})")
                        except Exception as e:
                            summary.append(f"- {f} (error reading file: {str(e)})")
            
            # Create the final summary
            final_summary = f"Found {total_files} files and {total_dirs} directories\n"
            final_summary += '\n'.join(summary)
            return final_summary
            
        except Exception as e:
            return f"Error reading directory: {str(e)}"

    def answer_query(self, query):
        """Answer a query about the current directory"""
        try:
            # Get directory information
            dir_info = self.get_directory_info()
            
            # Create prompt for the AI
            prompt = f"""Based on this directory information (including file contents):
            {dir_info}

            Answer this question: {query}

            Please provide a concise and relevant answer. You can use markdown formatting for:
            - Code blocks with ```
            - Lists with - or *
            - **Bold** or *italic* text
            - > Quotes
            
            Do not add any titles or headers at the beginning of your response."""

            # Generate title once before starting
            title = self.summarize_query(query)
            
            # Initialize response content and spinner
            content = ""
            spinner = Spinner("dots", text="Thinking...")
            
            # Create a live display with markdown rendering
            with Live(Panel(spinner, title=title, expand=False), refresh_per_second=10) as live:
                # Get streaming response from ollama
                stream = ollama.chat(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}],
                    stream=True
                )
                
                # Once we get the first chunk, switch from spinner to content
                for chunk in stream:
                    if 'message' in chunk:
                        if not content:  # First chunk
                            live.update(Panel(Markdown(content), title=title, expand=False))
                        content += chunk['message'].get('content', '')
                        # Update display with markdown-rendered content
                        live.update(Panel(Markdown(content), title=title, expand=False))
            
            return content
        except Exception as e:
            return f"Error processing query: {str(e)}"

    def summarize_query(self, query):
        """Create a concise title from the query using the AI model"""
        prompt = f"""Create a very short (3-5 words) title that captures the essence of this query: {query}.
        To give more context, the query is about the current directory and its contents."""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            title = response['message']['content'].strip().rstrip('.')
            return title
        except Exception:
            # Fallback to simple capitalization if AI fails
            title = query.rstrip('?').capitalize()
            return (title[:30] + '...') if len(title) > 30 else title


def main():
    agent = AIAgent()
    
    if len(sys.argv) < 2:
        # Use a default query for directory summary
        query = "Give me a one line summary of the current directory, with relevant file contents"
    else:
        query = sys.argv[1]
    
    # Process the query and display streaming output
    agent.answer_query(query)


if __name__ == "__main__":
    main()
