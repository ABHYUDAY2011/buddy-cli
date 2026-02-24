import os, sys, time, json, subprocess, ollama, pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()
CONFIG_DIR = os.path.join(os.environ['USERPROFILE'], '.buddy')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

# --- SMART CONFIG MANAGER ---
def load_config():
    # Defaulting to Qwen 0.5B as requested
    default = {"model": "qwen2.5:0.5b", "api_provider": "ollama", "api_key": "", "vision_model": "moondream"}
    if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR, exist_ok=True)
    
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f: json.dump(default, f)
        return default
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            # Auto-fix missing keys to prevent 'api_provider' System Error
            updated = False
            for key, value in default.items():
                if key not in config:
                    config[key] = value
                    updated = True
            if updated: save_config(config)
            return config
    except:
        return default

def save_config(config):
    with open(CONFIG_PATH, 'w') as f: json.dump(config, f, indent=4)

# --- PC CONTROL AGENT ---
def run_terminal(task_description, model):
    """Translates natural language to a clean PowerShell command."""
    prompt = f"Act as a Windows expert. Convert this to a one-line PowerShell command: '{task_description}'. Output ONLY the command. No talk, no backticks."
    try:
        res = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
        cmd = res['message']['content'].strip().replace('`', '').replace('powershell', '').strip()
        
        # Display what it wants to do
        console.print(Panel(f"[bold yellow]Proposed Command:[/bold yellow]\n[cyan]{cmd}[/cyan]", title="Terminal Agent"))
        
        if Confirm.ask("Run this command?"):
            proc = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            if proc.returncode == 0:
                return f"✅ Success:\n{proc.stdout}"
            else:
                return f"❌ Error:\n{proc.stderr}"
    except Exception as e: return f"Execution failed: {e}"
    return "Action skipped."

# --- ANIMATIONS ---
def startup_animation():
    console.clear()
    colors = ["cyan", "magenta", "yellow", "green", "blue", "bright_red"]
    banner = pyfiglet.figlet_format("BUDDY AI", font="slant")
    with Live(refresh_per_second=10) as live:
        for i in range(18):
            c = colors[i % len(colors)]
            live.update(Panel(Text(banner, style=f"bold {c}"), 
                        subtitle="[bold white]v2.9 - Agentic Qwen Edition[/bold white]", 
                        border_style=c))
            time.sleep(0.08)
    console.print("[dim]Type '/exit' to quit | '/model' for selector | '/api' for keys[/dim]\n")

def typewriter_print(text):
    for char in text:
        console.print(char, end="", style="bright_cyan")
        time.sleep(0.005)
    print("\n")

# --- MAIN LOOP ---
def main():
    config = load_config()
    startup_animation()

    while True:
        try:
            status = f"{config['api_provider']}:{config['model']}"
            user_input = Prompt.ask(f"\n[bold blue]buddy ({status}) >[/bold blue]")

            if user_input.lower() in ['/exit', 'exit', 'quit']:
                console.print("[bold red]Shutting down...[/bold red]")
                break

            # 1. COMMAND: Model Selector (Fixed Logic)
            if user_input.startswith('/model'):
                try:
                    res = ollama.list()
                    # Handle both dictionary and object formats
                    models = res.get('models', []) if isinstance(res, dict) else res.models
                    names = [m.get('name', m.get('model')) if isinstance(m, dict) else (m.name if hasattr(m, 'name') else m.model) for m in models]
                    
                    console.print("\n[bold yellow]Select a Model:[/bold yellow]")
                    for i, name in enumerate(names):
                        console.print(f" {i+1}. [cyan]{name}[/cyan]")
                    
                    choice = Prompt.ask("\nEnter number", choices=[str(i+1) for i in range(len(names))])
                    config['model'] = names[int(choice)-1]
                    save_config(config)
                    console.print(f"[green]Switched to {config['model']}[/green]")
                except Exception as e:
                    console.print(f"[red]Error fetching models: {e}[/red]")
                continue

            # 2. COMMAND: API & Provider Setup
            if user_input.startswith('/api'):
                providers = ["ollama", "google-gemini", "openai", "groq"]
                config['api_provider'] = Prompt.ask("Select Provider", choices=providers)
                if config['api_provider'] != "ollama":
                    config['api_key'] = Prompt.ask(f"Enter {config['api_provider']} API Key", password=True)
                save_config(config)
                continue

            # 3. PROCESSING
            with console.status("[bold yellow]Processing...", spinner="bouncingBar"):
                # Detect Terminal Tasks (Make, Create, Open, etc.)
                if any(k in user_input.lower() for k in ["make", "create", "open", "run", "folder", "notepad"]):
                    ans = run_terminal(user_input, config['model'])
                
                # Image Analysis
                elif any(ext in user_input.lower() for ext in [".jpg", ".png", ".jpeg"]):
                    path = user_input.split()[-1].strip('"')
                    if os.path.exists(path):
                        res = ollama.generate(model=config['vision_model'], prompt="Describe this image.", images=[open(path, 'rb').read()])
                        ans = res['response']
                    else:
                        ans = "Error: Image path not found."
                
                # Standard Chat
                else:
                    res = ollama.chat(model=config['model'], messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print("\n[bold magenta]Buddy:[/bold magenta]")
            typewriter_print(ans)

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

if __name__ == "__main__":
    main()


