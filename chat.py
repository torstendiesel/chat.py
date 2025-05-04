#!/usr/bin/env python3
import os
from datetime import datetime
from time import sleep
#def sleep(time):
    #return 0
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

def setup_log_file(model):
    # create logs dir if missing
    LOG_DIR = "logs"
    os.makedirs(LOG_DIR, exist_ok=True)
    # name your log by timestamp
    ts        = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path  = os.path.join(LOG_DIR, f"chat_{ts}.txt")
    # open handle in append mode
    log_file = open(log_path, "a", encoding="utf-8")
    # write a header
    log_file.write(f"Chat session started {datetime.now().isoformat()}\n")
    log_file.write(f"Model: {model}\n\n")
    return log_file

model_comparison = """Model comparison:
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
\n"""

def thanks(model):
    print(f"\n[bold yellow]{model}:[/bold yellow] You're welcome! If you need me again, just type \"chat\" into your terminal.")

def model_dialogue(cmd_parts, cmd, model):
    if len(cmd_parts) == 1:
        print(f"\nCurrent model: [cyan]{model}[/cyan]")
        print("Available:", ", ".join(ALLOWED_MODELS))
        print(model_comparison)
        return 0
    else:
        new_model = cmd_parts[1].strip()
        if new_model in ALLOWED_MODELS:
            model = new_model
            print(f"\n[bold green]Switched model to:[/bold green] {model}")
            return model
        else:
            print(f"\n[bold red]Error:[/bold red] '{new_model}' is not a valid model.")
            print("\nChoose from:", ", ".join(ALLOWED_MODELS))
            return 0

def import_files_as_context(user_input, log_file, messages):
    # Usage: /import <file1> [<file2> …]
    try:
        parts = shlex.split(user_input)
    except ValueError as e:
        print(f"\n[bold red]Error parsing command:[/bold red] {e}")
        #continue

    if len(parts) < 2:
        print("\nUsage: /import <file_path> [...]")
        #continue

    for raw_path in parts[1:]:
        file_path = os.path.expanduser(raw_path)
        if not os.path.isfile(file_path):
            print(f"\n[bold red]Error:[/bold red] File not found: {file_path}")
            #continue
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



def response(messages, log_file, term_width, model, console):
    # Most complex part of this program
    # Streams tokens as plaintext, then once we get the final response, clear all the lines of plaintext and replace them with markdown
    try:
        console.print(f"\n[bold green]{model} is thinking...[/bold green]")
        stream = client.responses.create(model=model, input=messages, stream=True)
        length_of_current_line = 0
        number_of_lines_in_output_so_far = 0
        output = ""
        for event in stream:
            if event.type == "response.output_text.delta":
                delta = event.delta
                sys.stdout.write(delta)
                sys.stdout.flush()
                length_of_current_line += len(delta)
                if delta.count('\n') > 0:
                    number_of_lines_in_output_so_far += delta.count('\n')
                    length_of_current_line = 0
                if length_of_current_line >= term_width:
                    number_of_lines_in_output_so_far += 1
                    length_of_current_line = 0
            if event.type == "response.output_text.done":
                answer = event.text
        for _ in range(number_of_lines_in_output_so_far + 2):
            sys.stdout.write('\033[2K')  # Clear the line
            sys.stdout.write('\033[F')  # Move cursor up
            sys.stdout.flush()
        console.print(f"\n[bold yellow]{model}:[/bold yellow]")
        console.print(Markdown(answer))
        print("")
        messages.append({"role": "assistant", "content": answer})
        log_file.write(f"{model}: {answer}\n\n")

    except OpenAIError as e:
        print(f"\n[bold red]OpenAI API Error:[/bold red] {e}")
        log_file.write(f"[ERROR] OpenAI API Error: {e}\n\n")
    except (KeyboardInterrupt, EOFError):
        print("")
        return 0
    except Exception as e:
        print(f"\n[bold red]Unexpected Error:[/bold red] {e}")
        log_file.write(f"[ERROR] Unexpected: {e}\n\n")


def loop(model, console, term_width, log_file, messages):

    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            print(f"/thanks")
            thanks(model)
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
                thanks(model)
                break

            if cmd == "model":
                model_selector = model_dialogue(cmd_parts, cmd, model)
                if model_selector: # returns 0 if no model chosen
                    model = model_selector
                continue
            
            if cmd == "usage":
                webbrowser.open("https://platform.openai.com/usage")
                continue

            if cmd == "import":
                import_files_as_context(user_input, log_file, messages)
                continue

            print(f"\n[bold red]Unknown command:[/bold red] /{cmd}")
            print("Available: /exit, /quit, /model, /usage")
            continue

        # Append the user's message
        messages.append({"role": "user", "content": user_input})

        # Response 
        response(messages, log_file, term_width, model, console)

def main():

    print("\n[grey50]/thanks to leave\n/model to switch models\n/import file1.txt (file2.txt)...\n/usage to view API usage[/grey50]\n")

    args = parse_args()
    model = args.model
    print(f"[bold yellow]{model}[/bold yellow]: How can I help you today?\n")

    console = Console()
    term_width = get_terminal_width() 
    log_file = setup_log_file(model);
    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    loop(model, console, term_width, log_file, messages)

    # Clean up
    log_file.write(f"\nChat session ended {datetime.now().isoformat()}\n")
    log_file.close()

if __name__ == "__main__":
    main()
