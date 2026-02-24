import os, sys, subprocess, json, time, threading, msvcrt, re
import ollama, pyfiglet, win32clipboard
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.prompt import Prompt, Confirm

# --- BOOTSTRAPPER ---
def bootstrap():
    reqs = ["ollama", "rich", "pyfiglet", "pywin32"]
    for p in reqs:
        try: __import__(p)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p, "--quiet"])

bootstrap()

console = Console()
CONFIG_DIR = os.path.join(os.environ['USERPROFILE'], '.buddy')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')
stop_response = False

def load_config():
    default = {"model": "qwen2.5:0.5b", "vision_model": "moondream", "theme": "green"}
    if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f: json.dump(default, f)
        return default
    with open(CONFIG_PATH, 'r') as f:
        return {**default, **json.load(f)}

# --- POLYGLOT FILE ENGINE ---
def save_code_to_file(code_content, language):
    # Mapping languages to correct Windows extensions
    ext_map = {
        "python": "py", "cpp": "cpp", "c++": "cpp", "c": "c", "java": "java", 
        "rust": "rs", "go": "go", "javascript": "js", "typescript": "ts",
        "html": "html", "css": "css", "powershell": "ps1", "bash": "sh",
        "ruby": "rb", "php": "php", "sql": "sql", "csharp": "cs", "c#": "cs"
    }
    ext = ext_map.get(language.lower(), "txt")
    timestamp = int(time.time())
    filename = f"buddy_code_{timestamp}.{ext}"
    
    if Confirm.ask(f"[bold green]Save this {language.upper()} code as [cyan]{filename}[/cyan]?[/bold green]"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_content)
        console.print(f"[bold green]✅ File created: {os.path.abspath(filename)}[/bold green]")

# --- TERMINAL / BASH ENGINE ---
def terminal_agent(task, model):
    sys_guide = "You are a Windows Automation Agent. Convert task to ONE-LINE PowerShell. Output ONLY raw command. No backticks."
    try:
        res = ollama.chat(model=model, messages=[{'role': 'system', 'content': sys_guide}, {'role': 'user', 'content': task}])
        cmd = res['message']['content'].strip().replace('`', '').replace('powershell', '').strip()
        console.print(Panel(f"[bold yellow]Bash Command:[/bold yellow]\n[bold cyan]{cmd}[/bold cyan]", title="🚀 Terminal Agent"))
        if Confirm.ask("Bash this into terminal?"):
            proc = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            return proc.stdout if proc.returncode == 0 else f"Error: {proc.stderr}"
    except Exception as e: return f"Agent Error: {e}"
    return "Cancelled."

# --- INTERRUPT LISTENER ---
def listen_for_esc():
    global stop_response
    while True:
        if msvcrt.kbhit() and msvcrt.getch() == b'\x1b':
            stop_response = True
        time.sleep(0.05)

# --- ADVANCED TYPEWRITER WITH CODE DETECTION ---
def typewriter(text):
    global stop_response
    stop_response = False
    
    # Split text into parts (Normal Text and Code Blocks)
    parts = re.split(r'(```\w*\n.*?\n```)', text, flags=re.DOTALL)
    
    for part in parts:
        if stop_response: break
        
        if part.startswith("```"):
            # Extract language and actual code content
            match = re.match(r'```(\w*)\n(.*?)\n```', part, re.DOTALL)
            if match:
                lang = match.group(1) or "txt"
                code = match.group(2)
                
                # Render syntax highlighted block
                syntax = Syntax(code, lang, theme="monokai", line_numbers=True, word_wrap=True)
                console.print("\n")
                console.print(Panel(syntax, title=f" {lang.upper()} SOURCE ", border_style="bold green"))
                
                # Prompt to save this specific block
                save_code_to_file(code, lang)
        else:
            # Type out normal conversational text
            for char in part:
                if stop_response:
                    console.print("\n[bold red][!] Muted by user.[/bold red]")
                    break
                console.print(char, end="", style="bright_cyan")
                time.sleep(0.005)
    print("\n")

def startup_animation():
    console.clear()
    banner = pyfiglet.figlet_format("BUDDY AI", font="slant")
    colors = ["cyan", "magenta", "yellow", "green", "blue"]
    with Live(refresh_per_second=10) as live:
        for i in range(15):
            c = colors[i % len(colors)]
            live.update(Panel(Text(banner, style=f"bold {c}"), subtitle="v6.0 - Polyglot Developer Agent | ESC to Mute", border_style=c))
            time.sleep(0.07)

# --- MAIN LOOP ---
def main():
    config = load_config()
    startup_animation()
    threading.Thread(target=listen_for_esc, daemon=True).start()

    while True:
        try:
            prompt_time = datetime.now().strftime('%H:%M')
            user_input = Prompt.ask(f"\n[bold magenta]buddy[/bold magenta][dim]@{prompt_time} >[/dim] ")

            if user_input.lower() in ['exit', 'quit']: break

            with console.status("[bold yellow]Buddy is thinking...", spinner="arc"):
                # Detect Terminal Tasks
                bash_triggers = ["make folder", "create folder", "delete", "open", "run", "check system"]
                
                if any(k in user_input.lower() for k in bash_triggers):
                    ans = terminal_agent(user_input, config['model'])
                else:
                    # General Chat or Code Request
                    res = ollama.chat(model=config['model'], messages=[{'role': 'user', 'content': user_input}])
                    ans = res['message']['content']

            console.print(f"\n[bold cyan]Buddy:[/bold cyan]")
            typewriter(ans)

        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

if __name__ == "__main__":
    main()

