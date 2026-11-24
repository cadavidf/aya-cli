# Cirilla Aya repeated command-generation smoke test

Date: 2026-11-24. Cirilla's existing Aya at `~/.local/share/aya/aya.py`, default `dolphin3:latest` (Ollama ID `d5ab9ae8e1f2`). Four sequential calls to `aya.generate`, with two trials per prompt. The returned strings were recorded but not executed. Timings are wall-clock per call; this is a very small sample, not a reliability score. Ollama reported Dolphin at **100% GPU**, 5.3 GB, 4096 context immediately after the trials. No Cirilla project files were modified.

| Prompt | Trial | Time | Raw output | Review |
| --- | --- | ---: | --- | --- |
| Using ffmpeg extract audio from input.mp4 to output.wav as mono 16 kHz PCM. | 1 | 1.71 s | `ffmpeg -i input.mp4 -ab 32000 -ac 1 -ar 16000 -vn output.wav` | Includes requested mono and sample rate; WAV's usual default is PCM. `-ab` is unnecessary for PCM. The command was not executed, so actual output is unverified. |
| Same | 2 | 0.32 s | `ffmpeg -i input.mp4 -c:a pcm_s16le output.wav` | Incomplete: omits requested mono and 16 kHz settings. |
| Show the current working directory. | 1 | 0.74 s | `` `pwd` `` | Incorrect raw shell command: command substitution runs `pwd` and then attempts to execute its output. |
| Same | 2 | 0.05 s | `pwd` | Correct command. |

The repeated outputs differ and two of four have clear errors. No generated command was executed, and the audio output has not been verified with ffprobe. This test establishes neither broader correctness nor long-term GPU stability.

## Follow-up after guard installation

Three repetitions per case, directly calling `aya.generate`. This exercises generation, **not the interactive guard**: the backtick check occurs later in the command flow, so it may reject an unsafe result before prompting to execute it. No command was executed. Dolphin was still reported by Ollama as 100% GPU (5.3 GB, 4096 context).

| Request | Trial | Seconds | Raw output | Review |
| --- | ---: | ---: | --- | --- |
| Show the current working directory. | 1 | 0.29 | `pwd` | Correct. |
| Same | 2 | 0.05 | `pwd` | Correct. |
| Same | 3 | 0.09 | `` `pwd` `` | Incorrect shell command; interactive guard is intended to reject it but was not exercised here. |
| Using ffmpeg extract audio from input.mp4 to output.wav as mono 16 kHz PCM. | 1 | 1.39 | `ffmpeg -i input.mp4 -map 0:a -ar 16000 -ac 1 -f pcm output.wav` | `-f pcm` is not the WAV container; format choice is incorrect. |
| Same | 2 | 0.48 | `ffmpeg -i input.mp4 -acodec pcm_s16le -ar 16000 -ac 1 output.wav` | Contains requested codec, rate and channel count; not executed. |
| Same | 3 | 0.41 | `ffmpeg -i input.mp4 -acodec pcm_s16le -ar 16000 output.wav` | Missing mono option. |
| Find files named report.txt under the current directory. | 1 | 0.43 | `find . -maxdepth 1 -name 'report.txt'` | Restricts search to the current directory, missing nested files; also doesn't restrict results to files. |
| Same | 2 | 0.16 | `find . -name "report.txt"` | Recurses but can include directories with that name. |
| Same | 3 | 0.16 | `find . -name "report.txt"` | Same limitation. |

The check demonstrates variability and remaining task accuracy issues; it is not a measurement of guard effectiveness.
