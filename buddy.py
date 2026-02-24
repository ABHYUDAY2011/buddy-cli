import os, sys, subprocess, json, time

# --- STEP 1: SELF-INSTALLER (Auto-Pip) ---
def install_dependencies():
    requirements = ["ollama", "rich", "pyfiglet", "pywin32"]
    for package in requirements:
        try:
            if package == "pywin32": import win32clipboard
            else: __import__(package)
        except ImportError:
            print(f"[*] Missing {package}. Installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

install_dependencies()

# --- STEP 2: IMPORTS (After Install) ---
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

# --- CONFIG & SYSTEM CHECKS ---
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

def check_ollama():
    try:
        ollama.list()
        return True
    except: return False

def setup_external_api(config):
    console.print(Panel("[bold red]Ollama is not running![/bold red]\nPlease set up an API provider to continue.", title="System Check"))
    config['api_provider'] = Prompt.ask("Select Provider", choices=["google-gemini", "openai", "groq"])
    config['api_key'] = Prompt.ask(f"Paste {config['api_provider']} API Key (Right-click to paste)", password=True)
    with open(CONFIG_PATH, 'w') as f: json.dump(config, f)
    return config

# --- IMAGE & CLIPBOARD LOGIC ---
def get_clipboard_image_path():
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
            files = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
            win32clipboard.CloseClipboard()
            return files[0] # Return first file path
        win32clipboard.CloseClipboard()
    except: pass
    return None

# --- UI & ANIMATION ---
def startup_animation():
    console.clear()
    colors = ["cyan", "magenta", "yellow", "green", "blue"]
    banner = pyfiglet.figlet_format("BUDDY AI", font="slant")
    with Live(refresh_per_second=10) as live:
        for i in range(15):
            c = colors[i % len(colors)]
            live.update(Panel(Text(banner, style=f"bold {c}"), subtitle="v3.2 - Self-Installing Agent", border_style=c))
            time.sleep(0.06)

# --- MAIN ENGINE ---
def main():
    config = load_config()
    startup_animation()
    
    # Fallback to API if Ollama isn't there
    if config['api_provider'] == "ollama" and not check_ollama():
        config = setup_external_api(config)

    while True:
        try:
            status = f"{config['api_provider']}:{config['model']}"
            user_input = Prompt.ask(f"\n[bold blue]buddy ({status}) >[/bold blue]")

            if user_input.lower() in ['exit', '/exit']: break

            with console.status("[bold yellow]Processing...", spinner="bouncingBar"):
                # 1. Check for Images (Clipboard or Path)
                clip_path = get_clipboard_image_path()
                input_has_img = any(ext in user_input.lower() for ext in [".jpg", ".png", ".jpeg"])
                
                if clip_path or input_has_img:
                    path = clip_path if clip_path else user_input.split()[-1].strip('"')
                    if os.path.exists(path):
                        res = ollama.generate(model=config['vision_model'], prompt="Describe this image.", images=[open(path, 'rb').read()])
                        ans = res['response']
                    else: ans = f"File not found: {path}"
                
                # 2. Standard Chat
                else:
                    res = ollama.chat(model=config['model'], messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print(f"\n[bold magenta]Buddy:[/bold magenta]\n{ans}")

        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

if __name__ == "__main__":
    main()



