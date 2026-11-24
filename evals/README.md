# Aya release 1 evaluation

Run `python3 ~/aya-evals/test_aya.py`. Set `AYA_SCRIPT` to test another copy.

These black-box checks run Aya in a temporary working directory and home folder,
using a fake Ollama and fake yt-dlp. They test startup, conversation history,
clearing history, command approval and execution, and YouTube cancellation. No
real model, network, or user files are used. They assess the CLI contract, not
the quality, latency, or tool-use reliability of an actual language model.
Real-model tasks should be evaluated separately.
# Command proposal benchmark

Run installed Ollama models sequentially with `python3 evals/benchmark_models.py --model dolphin3:latest --model MODEL_NAME --output eval-results.json`. The default limit is 90 seconds per task; adjust with `--timeout`. It uses Aya's actual command-generation prompt and prints each proposal and wall-clock time. It never executes generated commands. Component checks are preliminary: inspect proposals manually and validate any chosen command separately in an isolated fixture. Model loads and CPU contention can affect timing.
