Basically? I want to implement everything from the OpenAI API in a DIY, "Bring-Your-Own API key", yet fully-featured way. 

When I'm using a tool, I don't want to have to tinker with defaults -- I want to *either* be tinkering with it *or* using it to do real work. 

This has benefits beyond just for techies who want to be able to use chatgpt in the terminal. The free ChatGPT app doesn't let users pick what models they want, making them use roughly 5-20\* prompts on the "good" model before downgrading them to the cheaper model, until they wait 5 hours or so. If they know they don't need the biggest model, then it shouldn't give it to them to begin with, unless they specifically ask for it! (Of course, in exchange for this, they give it away for free.) 

In addition, there are genuinely useful tools locked away behind the API, which lack a good frontend. I transcribed a whole hour-long interview once with whisper-1 for three cents -- it would have taken me three hours without it! However, tools like this aren't easily accessible, which makes its usefulness a little bit trickier. I hope that this tool eventually makes these genuinely useful models more discoverable and usable. 

Lastly, the environmental cost of using AI tools is incredibly tricky to measure, especially on an individual level. However, if you assume that the entire cost (or some percentage, I'll do some research) of the API is being turned into electricity, then it's possible to use electricity costs to calculate the cost of inference or training of the models. Again, this would let users be more in-control of how much of an environmental cost their individual actions have. 

So, this tool will hopefully let both technically-minded folks and non-techies have better control over what AI models they are running, how much they want to pay for them, and give people a better sense of what the environmental impact is of using AI models, without the need for running models locally (like with ollama). 

Again, I want to more-or-less have feature parity with all of the API and all of the plus/pro/edu features of chatgpt, but pay-as-you-go. That means (eventually, including current bugs)...
 - voice input
 - real time api
 - better way of dealing with history (like a profile system -- loads all your previous chat conversations)
 - Including contexts (import a textbook on general relativity and ask a question about black holes, perhaps)
 - Temporary chats (less important because chat history is local and they don't train on API conversations)
 - Figure out how to better render equations
 - Fix long tables screwing up line clearing
 - Image generation
 - Better (more future-proof) model selector
 - Different model providers (gemini comes to mind)
 - config file (for easy api key access) 
 - Documentation
 - Tool Use: running python code, wolfram-alpha api, wikipedia api, web browsing, etc

\* I have not actually run this experiment, so this number is completely made up (but feels about right, based on vibes)
