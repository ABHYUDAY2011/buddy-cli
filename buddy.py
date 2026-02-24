import os, sys, time, json, subprocess, ollama, pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()
# Define paths correctly for Windows
CONFIG_DIR = os.path.join(os.environ['USERPROFILE'], '.buddy')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

# --- SMART CONFIG MANAGER (Fixes 'api_provider' and other KeyErrors) ---
def load_config():
    default = {
        "model": "gemma3:270m", 
        "api_provider": "ollama", 
        "api_key": "", 
        "vision_model": "moondream"
    }
    
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f: json.dump(default, f)
        return default
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            # Inject missing keys from default to prevent System Errors
            updated = False
            for key, value in default.items():
                if key not in config:
                    config[key] = value
                    updated = True
            if updated:
                with open(CONFIG_PATH, 'w') as f: json.dump(config, f)
            return config
    except Exception:
        return default

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

# --- TERMINAL AGENT ENGINE ---
def run_terminal_task(task_description, current_model):
    """Asks the AI to write a PowerShell command and then executes it."""
    prompt = f"Convert this request into a single PowerShell command: '{task_description}'. Return ONLY the command text, no markdown, no backticks, no talk."
    
    try:
        res = ollama.chat(model=current_model, messages=[{'role': 'user', 'content': prompt}])
        cmd = res['message']['content'].strip().replace('`', '')
        
        console.print(Panel(f"[bold yellow]Buddy proposes command:[/bold yellow]\n[cyan]{cmd}[/cyan]", title="Terminal Agent"))
        
        if Confirm.ask("Do you want Buddy to execute this?"):
            proc = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            if proc.returncode == 0:
                return f"✅ Success:\n{proc.stdout}"
            else:
                return f"❌ Error:\n{proc.stderr}"
        return "Action cancelled by user."
    except Exception as e:
        return f"Failed to generate command: {e}"

# --- UI & ANIMATIONS ---
def startup_animation():
    console.clear()
    colors = ["cyan", "magenta", "yellow", "green", "blue", "red"]
    banner_text = pyfiglet.figlet_format("BUDDY AI", font="slant")
    
    with Live(refresh_per_second=10) as live:
        for i in range(18):
            c = colors[i % len(colors)]
            live.update(Panel(Text(banner_text, style=f"bold {c}"), 
                        subtitle="[bold white]v2.7 - Agentic All-In-One[/bold white]", 
                        border_style=c))
            time.sleep(0.08)
    console.print("[dim]Type '/exit' to quit | '/models' to switch | '/api' for providers[/dim]\n")

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
            user_input = Prompt.ask(f"[bold blue]buddy ({status}) >[/bold blue]")

            if user_input.lower() in ['/exit', 'exit', 'quit']:
                console.print("[bold red]Shutting down... Goodbye![/bold red]")
                break

            # 1. COMMAND: Switch Models
            if user_input.startswith('/models'):
                try:
                    raw = ollama.list()
                    model_list = raw.get('models', []) if isinstance(raw, dict) else raw.models
                    names = [m.model if hasattr(m, 'model') else m['name'] for m in model_list]
                    
                    console.print("\n[bold yellow]Installed Ollama Models:[/bold yellow]")
                    for i, name in enumerate(names):
                        console.print(f" {i+1}. [green]{name}[/green]")
                    
                    choice = int(Prompt.ask("\nEnter number to select"))
                    config['model'] = names[choice-1]
                    config['api_provider'] = "ollama" # Auto-switch back to Ollama
                    save_config(config)
                    console.print(f"[bold green]Switched to {config['model']}[/bold green]")
                except Exception as e:
                    console.print(f"[red]Error fetching models: {e}[/red]")
                continue

            # 2. COMMAND: API Management
            if user_input.startswith('/api'):
                providers = ["ollama", "google-gemini", "openai", "groq"]
                config['api_provider'] = Prompt.ask("Select API Provider", choices=providers)
                if config['api_provider'] != "ollama":
                    config['api_key'] = Prompt.ask(f"Enter {config['api_provider']} API Key", password=True)
                save_config(config)
                console.print(f"[green]Provider updated to {config['api_provider']}[/green]")
                continue

            # 3. CORE PROCESSING
            with console.status("[bold yellow]Buddy is thinking...", spinner="bouncingBar"):
                # SYSTEM TASKS (Files, Folders, etc.)
                if any(k in user_input.lower() for k in ["make a file", "create folder", "run command", "open", "delete"]):
                    ans = run_terminal_task(user_input, config['model'])
                
                # IMAGE ANALYSIS (Checks for image paths)
                elif any(ext in user_input.lower() for ext in [".jpg", ".png", ".jpeg"]):
                    img_path = user_input.split()[-1].strip('"')
                    if os.path.exists(img_path):
                        res = ollama.generate(model=config['vision_model'], prompt="Describe this image in detail.", images=[open(img_path, 'rb').read()])
                        ans = res['response']
                    else:
                        ans = f"Could not find image at: {img_path}"
                
                # STANDARD CHAT
                else:
                    # Note: External APIs would require their specific SDKs here. 
                    # This version keeps Ollama as the primary engine.
                    res = ollama.chat(model=config['model'], messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print("\n[bold magenta]Buddy:[/bold magenta]")
            typewriter_print(ans)

        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

if __name__ == "__main__":
    main()


