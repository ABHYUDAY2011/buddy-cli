import time
import ollama
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.prompt import Prompt
from rich.text import Text

console = Console()

def startup_animation():
    """Startup animation."""
    console.clear()
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    with Live(Text("Initializing Buddy Systems...", style="bold cyan"), refresh_per_second=10) as live:
        for i in range(20):
            time.sleep(0.1)
            frame = frames[i % len(frames)]
            live.update(Text(f"{frame} Loading Buddy Agent...", style="bold cyan"))
    
    console.print(Panel.fit("[bold white]BUDDY CLI v1.0[/bold white]", border_style="blue", padding=(1, 10)))
    console.print("[dim]Powered by local Ollama models[/dim]\n")

def select_model():
    """Lists available Ollama models and lets the user choose one."""
    try:
        models = ollama.list()['models']
        model_names = [m['name'] for m in models]
        if not model_names:
            console.print("[bold red]No Ollama models found! Run 'ollama pull llama3' first.[/bold red]")
            return None
        
        console.print("[bold cyan]Available Models:[/bold cyan]")
        for i, name in enumerate(model_names):
            console.print(f" {i+1}. {name}")
        
        choice = Prompt.ask("\nSelect a model number", default="1")
        return model_names[int(choice) - 1]
    except Exception as e:
        console.print(f"[bold red]Error connecting to Ollama:[/bold red] {e}")
        return None

def main_loop():
    startup_animation()
    selected_model = select_model()
    if not selected_model: return

    console.print(f"\n[bold green]Connected to {selected_model}[/bold green]")
    console.print("[italic]Type 'exit' to quit.[/italic]\n")

    while True:
        # User input bar
        user_input = Prompt.ask("[bold blue]buddy >[/bold blue]")

        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print("[bold red]Shutting down... Goodbye![/bold red]")
            break

        # Thinking animation
        with console.status(f"[bold yellow]Buddy is thinking using {selected_model}...", spinner="bouncingBall"):
            try:
                response = ollama.chat(model=selected_model, messages=[{'role': 'user', 'content': user_input}])
                answer = response['message']['content']
                console.print(Panel(answer, title="[bold cyan]Buddy[/bold cyan]", border_style="white"))
            except Exception as e:
                console.print(f"[bold red]AI Error:[/bold red] {e}")

if __name__ == "__main__":
    main_loop()

