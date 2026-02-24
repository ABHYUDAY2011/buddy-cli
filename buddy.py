import os, sys, time, json, subprocess, ollama, pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()
CONFIG_DIR = os.path.join(os.environ['USERPROFILE'], '.buddy')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

# --- SMART CONFIG LOADER (Fixes 'api_provider' error) ---
def load_config():
    default = {"model": "gemma3:270m", "api_provider": "ollama", "api_key": "", "vision_model": "moondream"}
    if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR)
    
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f: json.dump(default, f)
        return default
    
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
        # Missing keys ko auto-fill karta hai bina crash kiye
        for key, value in default.items():
            if key not in config: config[key] = value
        return config

def save_config(config):
    with open(CONFIG_PATH, 'w') as f: json.dump(config, f)

# --- TERMINAL TASK EXECUTION ---
def run_terminal(task_description, model):
    prompt = f"Provide ONLY the PowerShell command to: {task_description}. No talk, no backticks."
    try:
        res = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
        cmd = res['message']['content'].strip().replace('`', '')
        if Confirm.ask(f"Buddy wants to run: [bold cyan]{cmd}[/bold cyan]. Allow?"):
            proc = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            return proc.stdout if proc.returncode == 0 else f"Error: {proc.stderr}"
    except Exception as e: return f"Execution failed: {e}"
    return "Action skipped."

# --- ANIMATION ---
def startup_animation():
    console.clear()
    colors = ["cyan", "magenta", "yellow", "green", "blue"]
    banner_text = pyfiglet.figlet_format("BUDDY AI", font="slant")
    with Live(refresh_per_second=10) as live:
        for i in range(15):
            c = colors[i % len(colors)]
            live.update(Panel(Text(banner_text, style=f"bold {c}"), subtitle="v2.6 - Agentic Edition", border_style=c))
            time.sleep(0.07)

# --- MAIN ENGINE ---
def main():
    config = load_config()
    startup_animation()

    while True:
        try:
            status = f"{config['api_provider']}:{config['model']}"
            user_input = Prompt.ask(f"\n[bold blue]buddy ({status}) >[/bold blue]")

            if user_input.lower() in ['/exit', 'exit']: break

            # 1. MODEL SELECTOR
            if user_input.startswith('/models'):
                models = [m['name'] for m in ollama.list()['models']]
                console.print("\n[bold yellow]Available Models:[/bold yellow]")
                for i, m in enumerate(models): console.print(f" {i+1}. {m}")
                idx = int(Prompt.ask("Select Number", choices=[str(i+1) for i in range(len(models))])) - 1
                config['model'] = models[idx]
                save_config(config)
                continue

            # 2. API SETUP
            if user_input.startswith('/api'):
                providers = ["ollama", "google-gemini", "openai"]
                config['api_provider'] = Prompt.ask("Select Provider", choices=providers)
                if config['api_provider'] != "ollama":
                    config['api_key'] = Prompt.ask(f"Enter {config['api_provider']} API Key", password=True)
                save_config(config)
                continue

            # 3. PROCESSING
            with console.status("[bold yellow]Thinking...", spinner="bouncingBar"):
                # File/System Tasks
                if any(word in user_input.lower() for word in ["make a file", "open", "run", "folder", "notepad"]):
                    ans = run_terminal(user_input, config['model'])
                # Image Analysis
                elif any(ext in user_input.lower() for ext in [".jpg", ".png", ".jpeg"]):
                    path = user_input.split()[-1].strip('"')
                    res = ollama.generate(model=config['vision_model'], prompt="Analyze", images=[open(path, 'rb').read()])
                    ans = res['response']
                # Standard Chat
                else:
                    res = ollama.chat(model=config['model'], messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print(f"\n[bold magenta]Buddy:[/bold magenta]\n{ans}")

        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

if __name__ == "__main__":
    main()
