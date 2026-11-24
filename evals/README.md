# Aya release 1 evaluation

Run `python3 ~/aya-evals/test_aya.py`. Set `AYA_SCRIPT` to test another copy.

These black-box checks run Aya in a temporary working directory and home folder,
using a fake Ollama and fake yt-dlp. They test startup, conversation history,
clearing history, command approval and execution, and YouTube cancellation. No
real model, network, or user files are used. They assess the CLI contract, not
the quality, latency, or tool-use reliability of an actual language model.
Real-model tasks should be evaluated separately.
