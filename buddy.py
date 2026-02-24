import os, sys, time, json, subprocess, ollama, pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()
CONFIG_PATH = os.path.join(os.environ['USERPROFILE'], '.buddy', 'config.json')

def load_config():
    default = {"model": "gemma3:270m", "api_provider": "ollama", "api_key": "", "vision_model": "moondream"}
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f: json.dump(default, f)
        return default
    with open(CONFIG_PATH, 'r') as f: return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f: json.dump(config, f)

def run_terminal(task_description):
    """Translates natural language to PowerShell and executes it."""
    config = load_config()
    prompt = f"Convert this request into a single PowerShell command: '{task_description}'. Return ONLY the command code, no backticks, no explanation."
    res = ollama.chat(model=config['model'], messages=[{'role': 'user', 'content': prompt}])
    cmd = res['message']['content'].strip().replace('`', '')
    
    if Confirm.ask(f"Buddy wants to run: [bold cyan]{cmd}[/bold cyan]. Allow?"):
        proc = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        if proc.returncode == 0:
            return f"Success: {proc.stdout}"
        else:
            return f"Error: {proc.stderr}. Analyzing fix..."
    return "Task cancelled."

def startup_animation():
    console.clear()
    colors = ["cyan", "magenta", "blue", "green", "yellow"]
    banner = pyfiglet.figlet_format("BUDDY AI", font="slant")
    for color in colors:
        console.clear()
        console.print(Panel(Text(banner, style=f"bold {color}"), subtitle="v2.5 - Agentic Multi-API", border_style=color))
        time.sleep(0.1)

def main():
    config = load_config()
    startup_animation()

    while True:
        try:
            current_status = f"{config['api_provider']}:{config['model']}"
            user_input = Prompt.ask(f"[bold blue]buddy ({current_status}) >[/bold blue]")

            if user_input.lower() in ['/exit', 'exit']: break

            # --- MODEL SELECTOR ---
            if user_input.startswith('/models'):
                try:
                    raw_models = ollama.list()
                    # Fix: Handle both dictionary and object responses from Ollama API
                    model_list = raw_models.get('models', []) if isinstance(raw_models, dict) else raw_models.models
                    names = [m.model if hasattr(m, 'model') else m['name'] for m in model_list]
                    
                    console.print("\n[bold yellow]Select a Model:[/bold yellow]")
                    for i, name in enumerate(names):
                        console.print(f" {i+1}. [cyan]{name}[/cyan]")
                    
                    choice = Prompt.ask("\nEnter number", choices=[str(i+1) for i in range(len(names))])
                    config['model'] = names[int(choice)-1]
                    save_config(config)
                    console.print(f"[green]Switched to {config['model']}[/green]")
                except Exception as e:
                    console.print(f"[red]Ollama Error: {e}[/red]")
                continue

            # --- API & PROVIDER SETUP ---
            if user_input.startswith('/api'):
                providers = ["ollama", "google-gemini", "openai", "groq"]
                config['api_provider'] = Prompt.ask("Select Provider", choices=providers)
                if config['api_provider'] != "ollama":
                    config['api_key'] = Prompt.ask(f"Enter {config['api_provider']} API Key", password=True)
                save_config(config)
                continue

            # --- SMART EXECUTION ---
            with console.status("[bold yellow]Processing...", spinner="dots"):
                # Detect file/PC tasks
                if any(k in user_input.lower() for k in ["make a file", "create folder", "open notepad", "run script"]):
                    ans = run_terminal(user_input)
                # Image Analysis
                elif any(ext in user_input.lower() for ext in [".jpg", ".png", ".jpeg"]):
                    path = user_input.split()[-1].strip('"') # Basic path extractor
                    res = ollama.generate(model=config['vision_model'], prompt="Describe this", images=[open(path, 'rb').read()])
                    ans = res['response']
                # Standard Chat
                else:
                    res = ollama.chat(model=config['model'], messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print("\n[bold magenta]Buddy:[/bold magenta]")
            console.print(ans)

        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

if __name__ == "__main__":
    main()


