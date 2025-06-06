# chat.py
Opinionated ChatGPT clone in the terminal with a nice UI

## Example usage
```
$ python3 chat.py

/thanks to leave
/model to switch models
/import file1.txt [file2.txt\]...
/usage to view API usage

gpt-4.1-nano: How can I help you today?

You: Write a haiku about key lime pie.    

gpt-4.1-nano:
Sweet tang in each bite,                                                        
Crimson crust and tender lime,                                                  
Summer’s creamy glow.                                                           

You: /thanks

gpt-4.1-nano: You're welcome! If you need me again, just type "chat" into your 
terminal.
```

## Installation
Git pull this repository, then to get dependencies run the following shell command:

```bash
pip install openai sys argparse shlex shutil rich
```

That aught to do the trick, make a new issue if you can't figure it out. 

## Features
- Choose various models (uses gpt-4.1-nano by default because it's cheap, but it's easy to switch mid-conversation)
- Looks almost as good as the normal chatGPT application
- Streams tokens, then re-renders it as markdown for the best of both worlds
- BYO Api key, you can use `/usage` to see API usage easily in the default browser
- Import multiple files for context
- Automatically thanks the model when you leave :)
- Easy-to-use, even for non-techies, easy to maintain for techies
- Automatically logs conversations
- GPL-3 licenced :)

## Anti-features
- I don't have the capacity to update this that often -- it works really well as of May 2025 but I can't promise updates
- Inputs aren't sanitized, and cannot be more than one line without probably breaking something
- Can't use up/down arrows to try different inputs on Linux
- No feature parity with normal chatGPT application yet: I haven't figured out image uploads, voice chat, memory, or customizing system prompts without editing the source code yet.
- Written with o4-mini anyways -- you could honestly probably make this yourself if you wanted to

## Purpose
This is more or less a test project, because I figured it would be easy enough to accomplish. I like ollama, but any useful model is too weak to run on my humble laptop. I also spent WAY too much time into making this work today, so I'm uploading it to github then I'm deleting it off my machine so that I can get some proper work done today :)
