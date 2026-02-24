import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
import time

console = Console()

def startup_animation():
    console.clear()
    # BIG GEMINI STYLE LOGO
    font = pyfiglet.Figlet(font='slant')
    logo = font.renderText('GEMINI')
    console.print(f"[bold cyan]{logo}[/bold cyan]")
    
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    with Live(Text("Initializing Buddy Systems...", style="bold magenta"), refresh_per_second=10) as live:
        for i in range(20):
            time.sleep(0.1)
            frame = frames[i % len(frames)]
            live.update(Text(f"{frame} Loading Buddy Agent v1.0...", style="bold magenta"))
    
    console.print(Panel.fit("✨ [bold white]BUDDY AI IS ONLINE[/bold white] ✨", style="bold green", border_style="bright_blue"))
    console.print("[dim]Type '/exit' to quit | Drag an image here to analyze[/dim]\n")

def typewriter_print(text):
    """Fixed typewriter effect without flush error."""
    for char in text:
        # console.print doesn't need flush=True, it handles it automatically
        console.print(char, end="", style="cyan")
        time.sleep(0.01)
    print("\n")
