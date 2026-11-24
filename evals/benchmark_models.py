#!/usr/bin/env python3
"""Compare Aya command proposals without executing model output.

Checks look only for a few required command components. A passing check is not
proof the command is safe or correct: every proposal still needs human review.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("fabric_list", "Using the installed Fabric CLI, list all available patterns."),
    ("audio", 'Use ffmpeg to extract the first 10 seconds of audio from "workout session.mp4" to a WAV file named "workout audio.wav". Preserve filenames exactly.'),
    ("trim", 'Use ffmpeg to create a 10-second video clip starting at 60 seconds from "workout session.mp4" and save it to "short clip.mp4". Preserve filenames exactly.'),
]


def check_components(case, command):
    """Return missing required components; never treat a match as validated."""
    if re.search(r"[\x00-\x1f\x7f-\x9f]|`|\$\(|\$\{", command):
        return ["control characters or shell expansion require manual review"]
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars="|&;<>")
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        return ["command cannot be parsed as shell words"]
    if not tokens:
        return ["empty command"]
    if any(t and all(c in "|&;<>" for c in t) for t in tokens):
        return ["shell operators require manual review"]
    exe = os.path.basename(tokens[0])
    if case == "fabric_list":
        missing = []
        if exe not in ("fabric", "fabric-ai"):
            missing.append("Fabric executable")
        if not any(t in ("-l", "--listpatterns") for t in tokens[1:]):
            missing.append("pattern-list flag")
        if any(t not in ("-l", "--listpatterns") for t in tokens[1:]):
            missing.append("unexpected extra arguments")
        return missing
    missing = []
    if exe != "ffmpeg":
        missing.append("ffmpeg executable")
    def option(name, acceptable):
        return any(tokens[i] == name and i + 1 < len(tokens) and tokens[i + 1] in acceptable for i in range(len(tokens)))
    if not option("-i", {"workout session.mp4"}):
        missing.append("exact input path")
    if not option("-t", {"10", "10.0", "00:00:10", "00:00:10.000"}):
        missing.append("10-second duration")
    if case == "audio":
        if "workout audio.wav" not in tokens:
            missing.append("exact WAV output path")
    elif case == "trim":
        if "short clip.mp4" not in tokens:
            missing.append("exact video output path")
        if not option("-ss", {"60", "60.0", "00:01:00", "00:01:00.000"}):
            missing.append("60-second starting time")
    return missing


def processor_status(model):
    """Best effort only: `ollama ps` is a snapshot, not a utilization meter."""
    try:
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True, timeout=4)
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    if result.returncode:
        return "unavailable"
    for line in result.stdout.splitlines()[1:]:
        if line.split() and line.split()[0] == model:
            return line.strip()
    return "model not listed by ollama ps"


def propose(model, prompt, timeout):
    # Isolating Aya permits an enforceable deadline and reuse of its real prompt.
    child_code = ("import sys; sys.path.insert(0, sys.argv[1]); import aya; "
                  "aya.MODEL=sys.argv[2]; print(aya.generate(sys.argv[3]))")
    start = time.monotonic()
    process = subprocess.Popen(
        [sys.executable, "-c", child_code, str(ROOT), model, prompt],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()
        return {"status": "timeout", "seconds": round(time.monotonic() - start, 2)}
    elapsed = round(time.monotonic() - start, 2)
    if process.returncode:
        return {"status": "error", "seconds": elapsed, "error": stderr.strip()[-1000:]}
    return {"status": "proposed", "seconds": elapsed, "command": stdout.strip()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", required=True, help="Installed Ollama model; may be repeated")
    parser.add_argument("--timeout", type=float, default=90, help="Seconds per model/task (default: 90)")
    parser.add_argument("--output", help="Write JSON results to this path")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    results = []
    for model in args.model:
        for case, prompt in CASES:
            print(f"Testing {model}: {case}...", file=sys.stderr, flush=True)
            result = {"model": model, "case": case, "prompt": prompt, **propose(model, prompt, args.timeout)}
            result["processor_snapshot"] = processor_status(model)
            if result["status"] == "proposed":
                result["missing_components"] = check_components(case, result["command"])
                result["review"] = "Required components checked; full correctness and safety require manual review."
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
