import os, sys, time, json, subprocess, ollama, pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()
CONFIG_PATH = os.path.join(os.environ['USERPROFILE'], '.buddy', 'config.json')

# --- CONFIGURATION ENGINE ---
def load_config():
    default = {"model": "gemma3:270m", "api_key": "", "vision_model": "moondream"}
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f: json.dump(default, f)
        return default
    with open(CONFIG_PATH, 'r') as f: return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f: json.dump(config, f)

# --- ADVANCED TERMINAL CONTROL ---
def run_command(cmd):
    """Executes a command and returns output. If it fails, Buddy tries to fix it."""
    console.print(f"[dim]Executing: {cmd}[/dim]")
    proc = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
    
    if proc.returncode != 0:
        console.print(f"[bold red]Error Detected![/bold red]")
        # Send error to AI for a fix
        fix_prompt = f"The command '{cmd}' failed with error: {proc.stderr}. Provide only the corrected PowerShell command."
        res = ollama.chat(model=load_config()['model'], messages=[{'role': 'user', 'content': fix_prompt}])
        suggested_fix = res['message']['content'].strip()
        
        if Confirm.ask(f"Buddy suggests fix: [bold green]{suggested_fix}[/bold green]. Run it?"):
            return run_command(suggested_fix)
    return proc.stdout

# --- UI & ANIMATION ---
def startup_animation():
    console.clear()
    colors = ["red", "orange3", "yellow", "green", "cyan", "blue", "purple"]
    banner_text = pyfiglet.figlet_format("BUDDY AI", font="slant")
    
    with Live(refresh_per_second=10) as live:
        for i in range(20):
            color = colors[i % len(colors)]
            live.update(Panel(Text(banner_text, style=f"bold {color}"), subtitle="[bold white]v2.0 - Agentic Edition[/bold white]"))
            time.sleep(0.08)
    console.print("[dim]Type '/exit' to quit | '/models' to switch | '/api' for keys[/dim]\n")

def typewriter_print(text):
    for char in text:
        console.print(char, end="", style="cyan")
        time.sleep(0.005)
    print("\n")

# --- MAIN ENGINE ---
def main():
    config = load_config()
    startup_animation()

    while True:
        try:
            user_input = Prompt.ask(f"[bold blue]buddy ({config['model']}) >[/bold blue]")

            # COMMAND HANDLERS
            if user_input.lower() in ['/exit', 'exit']: break
            
            if user_input.startswith('/models'):
                models = [m['name'] for m in ollama.list()['models']]
                console.print("[yellow]Available:[/yellow]", models)
                new_m = Prompt.ask("Choose model", choices=models)
                config['model'] = new_m
                save_config(config)
                continue

            if user_input.startswith('/api'):
                config['api_key'] = Prompt.ask("Enter API Key", password=True)
                save_config(config)
                console.print("[green]API Key Saved![/green]")
                continue

            # IMAGE DETECTION (Path or auto-analyze)
            img_path = None
            if any(ext in user_input.lower() for ext in [".jpg", ".png", ".jpeg"]):
                for word in user_input.split():
                    if os.path.exists(word.strip('"')):
                        img_path = word.strip('"')
                        user_input = user_input.replace(word, "").strip() or "Describe this image"
                        break

            # AI PROCESSING
            with console.status("[bold yellow]Thinking...", spinner="bouncingBar"):
                if img_path:
                    res = ollama.generate(model=config['vision_model'], prompt=user_input, images=[open(img_path, 'rb').read()])
                    ans = res['response']
                elif user_input.startswith(("run ", "do ", "execute ")):
                    # Extract command and run it
                    cmd = user_input.split(" ", 1)[1]
                    ans = run_command(cmd)
                else:
                    res = ollama.chat(model=config['model'], messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print("[bold magenta]Buddy:[/bold magenta]")
            typewriter_print(ans)

        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

if __name__ == "__main__":
    main()

