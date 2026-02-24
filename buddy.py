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
    # Big ASCII Logo
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
    """FIXED: Removed 'flush' to stop the crash."""
    for char in text:
        # Rich handles flushing automatically
        console.print(char, end="", style="cyan")
        time.sleep(0.01)
    print("\n")

def select_model():
    try:
        models = ollama.list()['models']
        model_names = [m['name'] for m in models]
        if not model_names: return "gemma3:270m"
        return model_names[0] # Default to first model
    except:
        return "gemma3:270m"

def main():
    startup_animation()
    active_model = select_model()
    console.print(f"[bold green]Using {active_model}[/bold green]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold blue]buddy >[/bold blue]")
            if user_input.lower() in ['/exit', 'exit', 'quit']: break

            img_path = None
            if any(ext in user_input.lower() for ext in [".jpg", ".png", ".jpeg"]):
                for word in user_input.split():
                    path = word.strip('"')
                    if os.path.exists(path):
                        img_path = path
                        user_input = user_input.replace(word, "").strip() or "Describe this image"
                        break

            with console.status("[bold yellow]Thinking...", spinner="dots"):
                if img_path:
                    res = ollama.generate(model='moondream', prompt=user_input, images=[open(img_path, 'rb').read()])
                    ans = res['response']
                else:
                    res = ollama.chat(model=active_model, messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print("[bold cyan]Buddy:[/bold cyan]")
            typewriter_print(ans)

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()

