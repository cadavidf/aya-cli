# Aya

Local terminal assistant powered by Ollama. Run `python3 aya.py` or use the `aya` shell command.

Ask questions conversationally. Use `/command <request>` to generate a shell command; Aya asks before execution. Paste a YouTube link for the existing video workflow. Use `/help` for commands and `/clear` to clear session history.

Run the isolated regression evaluations with `python3 evals/test_aya.py`.

Use `/inspect <question>` to let Aya inspect the current working directory with read-only listing, search, and file-reading tools. Its model-driven loop is limited to six steps and may fail when the model returns an invalid action. It does not edit files or execute commands.

Run all checks with `python3 -m unittest discover -s evals -p 'test_*.py'`.
