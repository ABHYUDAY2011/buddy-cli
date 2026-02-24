import ollama
import time
import sys
import os
import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt

console = Console()

def startup_animation():
    """BIG Gemini-style logo and startup sequence."""
    console.clear()
    
    # Render the big 'GEMINI' or 'BUDDY' text
    banner = pyfiglet.figlet_format("BUDDY AI", font="slant")
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    with Live(Text("Initializing Systems...", style="bold magenta"), refresh_per_second=10) as live:
        for i in range(15):
            time.sleep(0.1)
            frame = frames[i % len(frames)]
            live.update(Text(f"{frame} Connecting to Ollama Core...", style="bold magenta"))
    
    console.print(Panel.fit("✨ [bold white]BUDDY AI IS ONLINE[/bold white] ✨", style="bold green", border_style="bright_blue"))
    console.print("[dim]Type '/exit' to quit | Drag an image here to analyze[/dim]\n")

def typewriter_print(text):
    """Fixed: Removed 'flush' to stop the crash."""
    for char in text:
        # console.print handles flushing automatically for Rich
        console.print(char, end="", style="cyan")
        time.sleep(0.01)
    print("\n")


