#!/usr/bin/env python3
import os
from datetime import datetime
import sys
import argparse
import webbrowser
import shlex

# python-dotenv support (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Get OpenAI key from environment variable. 
def get_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("[bold red]Error:[/bold red] OPENAI_API_KEY not set.")
        print(" • export OPENAI_API_KEY=\"your_api_key\"")
        print(" • or put it in a .env file with OPENAI_API_KEY=your_api_key")
        sys.exit(1)
    return key

from openai import OpenAI

client = OpenAI(api_key=get_api_key())
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown

# for billing endpoints
from datetime import date
try:
    from openai.api_requestor import APIRequestor
except ImportError:
    APIRequestor = None

# Try to import the OpenAIError exception; if that fails, fall back to Exception.
try:
    from openai.error import OpenAIError
except (ImportError, ModuleNotFoundError):
    class OpenAIError(Exception):
        """Fallback if openai.error.OpenAIError isn't available."""
        pass

ALLOWED_MODELS = ["gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "o4-mini"]


def parse_args():
    p = argparse.ArgumentParser(
        description="CLI chat with OpenAI models (default=gpt-4.1-nano)"
    )
    p.add_argument(
        "-m", "--model",
        choices=ALLOWED_MODELS,
        default="gpt-4.1-nano",
        help="Which model to use"
    )
    return p.parse_args()

def main():
    console = Console()
    args = parse_args()
    model = args.model

    # ─── SETUP LOG FILE ───────────────────────────
    # create logs dir if missing
    LOG_DIR = "logs"
    os.makedirs(LOG_DIR, exist_ok=True)
    # name your log by timestamp
    ts        = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path  = os.path.join(LOG_DIR, f"chat_{ts}.txt")
    # open handle in append mode
    log_file  = open(log_path, "a", encoding="utf-8")
    # write a header
    log_file.write(f"Chat session started {datetime.now().isoformat()}\n")
    log_file.write(f"Model: {model}\n\n")
    # ────────────────────────────────────────────────

    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    # print(f"\n[grey50]Model:[/grey50] [cyan]{model}[/cyan]")
    print("\n[grey50]/thanks to leave\n/model to switch models\n/import file1.txt \[file2.txt\]...\n/usage to view API usage[/grey50]\n")

    print(f"[bold yellow]{model}[/bold yellow]: How can I help you today?\n")
    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            print(f"/thanks")
            print(f"\n[bold yellow]{model}:[/bold yellow] You're welcome! If you need me again, just type \"chat\" into your terminal.")
            break

        if not user_input.strip():
            continue

        # log user message
        log_file.write(f"You: {user_input}\n")

        # Slash-command handling
        if user_input.startswith("/"):
            cmd_parts = user_input.strip().split(maxsplit=1)
            cmd = cmd_parts[0][1:].lower()

            if cmd in ("thanks"):
                print(f"\n[bold yellow]{model}:[/bold yellow] You're welcome! If you need me again, just type \"chat\" into your terminal.")
                break

            if cmd == "model":
                if len(cmd_parts) == 1:
                    print(f"\nCurrent model: [cyan]{model}[/cyan]")
                    print("Available:", ", ".join(ALLOWED_MODELS))
                    print("""Model comparison:
gpt-4.1: Flagship GPT model for complex tasks. 
gpt-4.1-mini: Balanced for intelligence, speed, and cost
gpt-4.1-nano (default): Fastest, most cost-effective GPT-4.1 model
o4-mini: Faster, more affordable reasoning model

| Model        | Intelligence    | Speed | Price (Input/Output per 1M tokens) |
|--------------|-----------------|-------|------------------------------------|
| gpt-4.1      | 4/5             | 3/5   | $2.00 / $8.00                      |
| gpt-4.1-mini | 3/5             | 4/5   | $0.40 / $1.60                      |
| gpt-4.1-nano | 2/5             | 5/5   | $0.10 / $0.40                      |
| o4-mini      | 4/5 (Reasoning) | 3/5   | $1.10 / $4.40                      |
\n""")
                else:
                    new_model = cmd_parts[1].strip()
                    if new_model in ALLOWED_MODELS:
                        model = new_model
                        print(f"\n[bold green]Switched model to:[/bold green] {model}")
                    else:
                        print(f"\n[bold red]Error:[/bold red] '{new_model}' is not a valid model.")
                        print("\nChoose from:", ", ".join(ALLOWED_MODELS))
                continue
            
            if cmd == "usage":
                webbrowser.open("https://platform.openai.com/usage")
                continue

            if cmd == "import":
                # Usage: /import <file1> [<file2> …]
                try:
                    parts = shlex.split(user_input)
                except ValueError as e:
                    print(f"\n[bold red]Error parsing command:[/bold red] {e}")
                    continue

                if len(parts) < 2:
                    print("\n[bold red]Error:[/bold red] Usage: /import <file_path> [...]")
                    continue

                for raw_path in parts[1:]:
                    file_path = os.path.expanduser(raw_path)
                    if not os.path.isfile(file_path):
                        print(f"\n[bold red]Error:[/bold red] File not found: {file_path}")
                        continue
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        header = f"<Imported file {file_path}>"
                        messages.append({
                            "role": "user",
                            "content": f"{header}\n\n{content}"
                        })
                        print(f"\n[bold green]Imported:[/bold green] {file_path}")
                        log_file.write(f"You imported {file_path}:\n{content}\n\n")
                    except Exception as e:
                        print(f"\n[bold red]Error reading {file_path}:[/bold red] {e}")
                continue

            print(f"\n[bold red]Unknown command:[/bold red] /{cmd}")
            print("Available: /exit, /quit, /model, /usage")
            continue

        # Append the user's message
        messages.append({"role": "user", "content": user_input})

        try:
            with console.status(f"[bold yellow]{model} is thinking...[/bold yellow]", spinner="dots"):
                resp = client.chat.completions.create(model=model,
                messages=messages)
            answer = resp.choices[0].message.content
            console.print(f"\n[bold yellow]{model}:[/bold yellow]")
            console.print(Markdown(answer))
            print("")
            messages.append({"role": "assistant", "content": answer})

            # log AI response
            log_file.write(f"{model}: {answer}\n\n")

        except OpenAIError as e:
            print(f"\n[bold red]OpenAI API Error:[/bold red] {e}")
            log_file.write(f"[ERROR] OpenAI API Error: {e}\n\n")
        except Exception as e:
            print(f"\n[bold red]Unexpected Error:[/bold red] {e}")
            log_file.write(f"[ERROR] Unexpected: {e}\n\n")

    # ─── CLEAN UP ──────────────────────────────────
    log_file.write(f"\nChat session ended {datetime.now().isoformat()}\n")
    log_file.close()

if __name__ == "__main__":
    main()
