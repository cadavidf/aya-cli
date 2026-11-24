# Aya project checkpoint

Updated: 2026-11-24

## Current stage

Stage 1: evaluating less-restricted open-weight models on the iMac CPU. Gemma 3 4B and Mistral 7B GGUF candidates have downloaded, loaded on CPU, and completed an initial three-task benchmark. Further repeated tests are needed for reliability.

## Known working version

- `aya` launches `~/aya/aya.py`; the default is `dolphin3:latest`. An installed model can be selected for one session with `AYA_MODEL=model-name aya`.
- Git commit `ab70c3b` includes the model override and comparison harness.
- `python3 -m unittest discover -s evals -p 'test_*.py'` passed 16 tests.
- Aya can chat, generate commands behind explicit approval, and perform bounded read-only inspection via `/inspect`; it cannot yet autonomously edit projects.

## Evaluation evidence

See `evals/benchmark-2026-11-24.md` and `evals/live-results-2026-11-24.md`. On Dolphin CPU, Fabric listing and a controlled WAV extraction succeeded; the proposed stream-copy trim produced audio but no video. Mistral wrapped commands in backticks and selected the wrong audio interval; Gemma failed the two FFmpeg proposals. Both candidates ran on CPU, and this was one run per task, not a reliability score.

The same benchmark is `python3 evals/benchmark_models.py --model MODEL --timeout 60 --output /private/tmp/aya-model-results.json`. It does not execute generated commands. Inspect and verify outputs manually in isolated fixtures.

## Resume

1. Candidate model names (both now downloaded):
   - `hf.co/mlabonne/gemma-3-4b-it-abliterated-v2-GGUF:Q4_K_M`
   - `hf.co/noctrex/Mistral-7B-Instruct-v0.3-abliterated-GGUF:Q4_K_M`
2. Repeat and expand the benchmark sequentially, including real workout workflow and adversarial cases. Record failures and timeouts. Review before executing any command. No candidate is yet a proven reliable agent.
3. Improve Aya's handling of model formatting and execution feedback, then re-run the evaluations and compare. Update this checkpoint and commit results.
4. Investigate GPU support only as the separate Stage 4 experiment; don't assume smaller weights resolve the Metal/backend reset issue.
