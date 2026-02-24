import ollama
import time
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown

console = Console()

def startup_animation():
    """Startup sequence like modern AI agents."""
    console.clear()
    with console.status("[bold cyan]Initializing Buddy Agent...", spinner="point"):
        time.sleep(1)
    console.print(Text("Buddy CLI v1.0.0", style="bold white"))
    console.print(Text("Type /help for commands.", style="dim italic"))
    console.print("")

def typewriter_stream(response_text):
    """Simulates real-time streaming output."""
    with Live(Text("", style="cyan"), auto_refresh=False) as live:
        full_text = ""
        for char in response_text:
            full_text += char
            live.update(Text(full_text, style="cyan"))
            live.refresh()
            time.sleep(0.005)
    print("\n")

def show_help():
    help_text = """
    [bold cyan]Available Commands:[/bold cyan]
    /help       - Show this menu
    /image      - Analyze an image (Usage: /image <path> <prompt>)
    /clear      - Clear the screen
    /exit       - Close Buddy
    """
    console.print(Panel(help_text, border_style="dim", title="Help Center"))

def chat_loop():
    startup_animation()
    while True:
        try:
            # Gemini-style interactive prompt
            user_input = Prompt.ask("[bold blue]buddy >[/bold blue]").strip()
            if not user_input: continue
            
            # --- Slash Commands ---
            if user_input.startswith('/'):
                parts = user_input.split()
                cmd = parts[0].lower()
                if cmd == '/exit': break
                elif cmd == '/help': show_help(); continue
                elif cmd == '/clear': console.clear(); continue
                elif cmd == '/image':
                    if len(parts) < 2:
                        console.print("[red]Error: Path missing. Use: /image <path> <prompt>[/red]")
                        continue
                    img_path = parts[1].strip('"')
                    prompt = " ".join(parts[2:]) if len(parts) > 2 else "Describe this image."
                    if not os.path.exists(img_path):
                        console.print(f"[red]Error: File not found: {img_path}[/red]")
                        continue
                    with console.status("[bold yellow]Analyzing...", spinner="arc"):
                        with open(img_path, 'rb') as f:
                            res = ollama.generate(model='moondream', prompt=prompt, images=[f.read()])
                            typewriter_stream(res['response'])
                    continue

            # --- Text Chat (Gemma 3) ---
            with console.status("[bold cyan]Thinking...", spinner="dots"):
                # Uses Gemma 3 for efficient local text processing
                res = ollama.chat(model='gemma3:270m', messages=[{'role': 'user', 'content': user_input}])
                typewriter_stream(res['message']['content'])

        except KeyboardInterrupt:
            console.print("\n[red]Session ended.[/red]")
            break
        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

if __name__ == "__main__":
    chat_loop()
