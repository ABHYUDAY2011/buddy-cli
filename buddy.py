import os, sys, subprocess, json, time

# --- STEP 1: AUTO-DEPENDENCY CHECK ---
def install_deps():
    reqs = ["ollama", "rich", "pyfiglet", "pywin32"]
    for package in reqs:
        try:
            if package == "pywin32": import win32clipboard
            else: __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

install_deps()

# --- STEP 2: IMPORTS ---
import ollama
import pyfiglet
import win32clipboard
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()
CONFIG_DIR = os.path.join(os.environ['USERPROFILE'], '.buddy')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

# --- CONFIG ENGINE ---
def load_config():
    default = {"model": "qwen2.5:0.5b", "api_provider": "ollama", "api_key": "", "vision_model": "moondream"}
    if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f: json.dump(default, f)
        return default
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
        for k, v in default.items():
            if k not in config: config[k] = v
        return config

def save_config(config):
    with open(CONFIG_PATH, 'w') as f: json.dump(config, f, indent=4)

# --- TERMINAL & CLIPBOARD TOOLS ---
def get_clip():
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
            path = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)[0]
            win32clipboard.CloseClipboard()
            return path
        win32clipboard.CloseClipboard()
    except: pass
    return None

def run_pc_task(task, model):
    sys_msg = "You are a Windows Expert. Convert request to ONE-LINE PowerShell. Output ONLY command. No talk, no backticks."
    try:
        res = ollama.chat(model=model, messages=[{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': task}])
        cmd = res['message']['content'].strip().replace('`', '').replace('powershell', '').split('\n')[0]
        console.print(Panel(f"[bold yellow]Task:[/bold yellow] {cmd}", title="Terminal Agent"))
        if Confirm.ask("Execute?"):
            proc = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, timeout=10)
            return proc.stdout if proc.returncode == 0 else f"Error: {proc.stderr}"
    except: return "Task failed."
    return "Skipped."

# --- ANIMATION ---
def startup():
    console.clear()
    colors = ["cyan", "magenta", "yellow", "green", "blue"]
    banner = pyfiglet.figlet_format("BUDDY AI", font="slant")
    with Live(refresh_per_second=10) as live:
        for i in range(15):
            c = colors[i % len(colors)]
            live.update(Panel(Text(banner, style=f"bold {c}"), subtitle="v3.3 - Agentic & Vision", border_style=c))
            time.sleep(0.06)
    console.print("[dim]Commands: /model | /api | /exit[/dim]\n")

# --- MAIN LOOP ---
def main():
    config = load_config()
    startup()

    while True:
        try:
            status = f"{config['api_provider']}:{config['model']}"
            user_input = Prompt.ask(f"\n[bold blue]buddy ({status}) >[/bold blue]")

            if user_input.lower() in ['exit', '/exit']: break

            # --- GLOBAL COMMANDS ---
            if user_input.startswith('/model'):
                try:
                    res = ollama.list()
                    models = res.get('models', []) if isinstance(res, dict) else res.models
                    names = [m.get('name', m.get('model')) if isinstance(m, dict) else m.model for m in models]
                    console.print("\n[yellow]Select Model:[/yellow]")
                    for i, n in enumerate(names): console.print(f" {i+1}. {n}")
                    idx = int(Prompt.ask("Enter number")) - 1
                    config['model'] = names[idx]
                    save_config(config)
                    console.print(f"[green]Switched to {config['model']}[/green]")
                except: console.print("[red]Ollama not running for model list.[/red]")
                continue

            if user_input.startswith('/api'):
                config['api_provider'] = Prompt.ask("Select Provider", choices=["ollama", "google-gemini", "openai"])
                if config['api_provider'] != "ollama":
                    config['api_key'] = Prompt.ask("Paste API Key (Right-click)", password=True)
                save_config(config); continue

            # --- PROCESSING ---
            with console.status("[bold yellow]Thinking...", spinner="bouncingBar"):
                clip_path = get_clip()
                # Image detection
                if clip_path and any(clip_path.lower().endswith(ex) for ex in [".jpg",".png",".jpeg"]):
                    res = ollama.generate(model=config['vision_model'], prompt="Describe this.", images=[open(clip_path, 'rb').read()])
                    ans = res['response']
                # PC Task detection
                elif any(k in user_input.lower() for k in ["make", "create", "open", "run", "delete"]):
                    ans = run_pc_task(user_input, config['model'])
                # Default Chat
                else:
                    res = ollama.chat(model=config['model'], messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print(f"\n[bold magenta]Buddy:[/bold magenta]\n{ans}")

        except Exception as e: console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()


