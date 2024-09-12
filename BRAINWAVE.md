
**Meetup Event**   
https://www.meetup.com/brain-wave-collective/events/303008768

**Blog**  
https://phoenix.arize.com/

**Live Demo**  
https://phoenix-demo.arize.com/projects

**Docs**  
https://docs.arize.com/phoenix

**GitHub**  
[https://github.com/**Arize-ai**/phoenix](https://github.com/Arize-ai/phoenix)  
[https://github.com/**brainwavecollective**/phoenix (🧠🌊 fork, this repo)](https://github.com/brainwavecollective/phoenix)  

## Install/Setup
```
# Using RunPod.io: "RTX 2000 ada" in terminal, but this is likely a similar process for other environments
# Runpod is not necessary for low GPU utilization needs, so this should be the same process locally

# TBD: setup a venv instead of running as root

# Basic env setup
python -m pip install --upgrade pip

# Install Phoenix (handled in example notebook)
#pip install arize-phoenix

# Get the code for this repo
cd /workspace
git clone https://github.com/brainwavecollective/phoenix.git
cd phoenix
git checkout docs

# Start server 
# NOT necessary w/notebook
# After launch phoenix command the Connect option will become available 
#python3 -m phoenix.server.main serve


```

## Quickstart

**Prerequisites**  
You will need an [https://platform.openai.com/api-keys](OpenAI API Key). Note that this is a separate billing account from the $20/month plan, and will typically require a pre-payment of some amount (the default amount is $10).

In your Jupyter server workspace, navigate to:  
 - phoenix/tutorials/quickstart/BWC_tracing_quickstart_openai.ipynb



TBD: runpod expose port for UI, needs to be setup before starting pod (template) 
TBD: look into persistent storage (github/etc?)

