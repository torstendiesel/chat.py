#!/usr/bin/env python3
import os
from datetime import datetime
#from time import sleep
def sleep(time):
    return 0
import sys
import argparse
import webbrowser
import shlex
import shutil

from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown

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

def get_terminal_width():
    return shutil.get_terminal_size((80, 20)).columns  # default to 80 if undetectable

def estimate_display_lines(text: str, width: int) -> int:
    lines = text.split('\n')
    total_lines = 0
    for line in lines:
        # Estimate wrapped lines
        total_lines += (len(line) // width) + 1
    return total_lines

def main():
    console = Console()
    args = parse_args()
    model = args.model
    term_width = get_terminal_width() 

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
    print("\n[grey50]/thanks to leave\n/model to switch models\n/import file1.txt (file2.txt)...\n/usage to view API usage[/grey50]\n")

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

        # Response 
        try:
            console.print(f"\n[bold yellow]{model} is thinking...[/bold yellow]")
            stream = client.responses.create(model=model, input=messages, stream=True)
            output_length = 0
            output_buffer = ""
            for event in stream: 
                #print(event.type)
                if event.type == "response.output_text.delta":
                    #print(event)
                    output_length += len(event.delta)
                    output_buffer += event.delta
                    sys.stdout.write(event.delta)
                    sys.stdout.flush()
                    sleep(0.05)
#                    if event.type == "response.output_text.done":
#                        sys.stdout.write('\b' * len(live_buffer) + ' ' * len(live_buffer))
#                        sys.stdout.flush()
#                        #console.clear()
#                        answer = event.text
                #print(stream)
                #answer = stream.output_item.done
            #lines = output_buffer.count('\n') + 2
            lines_to_clear = estimate_display_lines(output_buffer, term_width) + 1
            for _ in range(lines_to_clear):
                sys.stdout.write('\033[F')  # Move cursor up
                #sys.stdout.write(' ' * 100)  # Clear the line
                sys.stdout.write('\033[K')  # Clear the line
                sys.stdout.flush()
                sleep(0.5)
            answer = output_buffer
            # sys.stdout.write('\b' * output_length + ' ' * output_length)
            # sys.stdout.flush()
            console.print(f"\n[bold yellow]{model}:[/bold yellow]")
            console.print(Markdown(answer))
            print("")
            messages.append({"role": "assistant", "content": answer})

#def chatstream(list):
#     strlen = 0
#     output_buffer = ""
#     for entry in list:
#         strlen += len(entry)
#         output_buffer += entry
#         sys.stdout.write(entry)
#         sys.stdout.flush()
#         sleep(0.1)
#     sys.stdout.write('\b' * strlen + output_buffer.upper() + '\n')
#     sys.stdout.flush()

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
