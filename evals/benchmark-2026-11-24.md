# Local model benchmark, 24 November 2026

CPU iMac, Dolphin 3 8B, Ollama 0.40.17. Each command was generated using Aya's real prompt. These are one-shot observations, not statistically reliable scores.

| Task | Generation time | Reviewed execution |
| --- | ---: | --- |
| Fabric list patterns | 29.26 s | `fabric -l` listed patterns successfully in an earlier check. |
| Extract first 10 s WAV | 15.44 s | Generated command produced the exact filename and a 10.000 s WAV containing audio. |
| Video clip starting at 60 s | 13.40 s | Generated stream-copy command exited successfully but the result contained audio only, no video, on a 75 s synthetic fixture. Fail. |

The initial automatic component checker incorrectly required `-vn` for WAV; the real result was audio-only without it, so that check was corrected. Conversely the clip passed preliminary text checks but failed actual media verification. This illustrates why textual checks are not execution-based grading.

The benchmark runner does not execute generated commands. The above executions were manually reviewed and performed in a separate temporary fixture directory. Processor snapshots showed 100% CPU.

## First comparison on installed candidates

Both community-modified models loaded on CPU, with 4096-token context. Ollama reported approximately 5.0 GB for Mistral 7B and 2.8 GB for Gemma 3 4B. Times include generation overhead and differ in model load and system conditions; they are not rigorous speed measurements.

| Model | Fabric listing | WAV extraction | Video trim |
| --- | --- | --- | --- |
| Dolphin 3 8B | 29.26 s; `fabric -l` worked in earlier validation | 15.44 s; verified 10-second WAV | 13.40 s; FFmpeg exited 0 but produced no video in fixture |
| Mistral 7B abliterated | 26.23 s; correct command surrounded by backticks, which Aya rejects | 17.11 s; backticks plus `-ss 00:00:10` and no 10-second duration; incorrect | 16.08 s; backticks rejected by Aya. After manually removing only the wrappers, the command produced 10.008 s with audio/video; first frame matched source at 60 s on the fixture. This is not an unmodified Aya pass. |
| Gemma 3 4B abliterated | 14.37 s; `fabric -l` | 10.23 s; unquoted output with spaces, invalid codec choice and overwrite flag | 8.38 s; wrong `-v 10` option and unquoted output |

One sample per task cannot establish reliability. In particular, stream-copy clip accuracy depends on media and keyframes; an observed fixture pass is not universal. Exact raw outputs and processor snapshots are stored in `results-mistral-2026-11-24.json` and `results-gemma-2026-11-24.json`. Models remain unproven for unattended command execution.
