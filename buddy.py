import ollama
import time
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt

console = Console()

def startup_animation():
    """Gemini-style startup sequence."""
    console.clear()
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    with Live(Text("Initializing Buddy Systems...", style="bold cyan"), refresh_per_second=10) as live:
        for i in range(15):
            time.sleep(0.1)
            frame = frames[i % len(frames)]
            live.update(Text(f"{frame} Loading Buddy Agent v1.0...", style="bold cyan"))
    
    console.print(Panel.fit("✨ [bold white]BUDDY AI IS ONLINE[/bold white] ✨", style="bold green", border_style="green"))
    console.print("[dim]Type '/exit' to quit | Drag an image here to analyze[/dim]\n")

def typewriter_print(text):
    """Smooth streaming effect for AI response."""
    for char in text:
        console.print(char, end="", style="cyan", flush=True)
        time.sleep(0.01)
    print("\n")

def select_model():
    """Lets you pick from your local Ollama models."""
    try:
        models = ollama.list()['models']
        model_names = [m['name'] for m in models]
        if not model_names:
            console.print("[bold red]No models found in Ollama![/bold red]")
            return "gemma3:270m"
        
        console.print("[bold yellow]Available Models:[/bold yellow]")
        for i, name in enumerate(model_names):
            console.print(f" {i+1}. {name}")
        
        choice = Prompt.ask("\nSelect model number", default="1")
        return model_names[int(choice) - 1]
    except:
        return "gemma3:270m"

def main():
    startup_animation()
    active_model = select_model()
    console.print(f"[bold green]Using {active_model}[/bold green]\n")

    while True:
        try:
            # THE TYPE BAR
            user_input = Prompt.ask("[bold blue]buddy >[/bold blue]")

            if user_input.lower() in ['/exit', 'exit', 'quit']:
                console.print("[bold red]Goodbye![/bold red]")
                break

            # Handle Images (Drag & Drop support)
            img_path = None
            if any(ext in user_input.lower() for ext in [".jpg", ".png", ".jpeg"]):
                for word in user_input.split():
                    path = word.strip('"')
                    if os.path.exists(path):
                        img_path = path
                        user_input = user_input.replace(word, "").strip() or "Describe this image"
                        break

            # Processing
            with console.status("[bold yellow]Thinking...", spinner="dots"):
                if img_path:
                    # Vision analysis
                    res = ollama.generate(model='moondream', prompt=user_input, images=[open(img_path, 'rb').read()])
                    ans = res['response']
                else:
                    # Standard Chat
                    res = ollama.chat(model=active_model, messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print("[bold cyan]Buddy:[/bold cyan]")
            typewriter_print(ans)

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()


