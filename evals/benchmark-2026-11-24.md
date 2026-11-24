# Local model benchmark, 24 November 2026

CPU iMac, Dolphin 3 8B, Ollama 0.40.17. Each command was generated using Aya's real prompt. These are one-shot observations, not statistically reliable scores.

| Task | Generation time | Reviewed execution |
| --- | ---: | --- |
| Fabric list patterns | 29.26 s | `fabric -l` listed patterns successfully in an earlier check. |
| Extract first 10 s WAV | 15.44 s | Generated command produced the exact filename and a 10.000 s WAV containing audio. |
| Video clip starting at 60 s | 13.40 s | Generated stream-copy command exited successfully but the result contained audio only, no video, on a 75 s synthetic fixture. Fail. |

The initial automatic component checker incorrectly required `-vn` for WAV; the real result was audio-only without it, so that check was corrected. Conversely the clip passed preliminary text checks but failed actual media verification. This illustrates why textual checks are not execution-based grading.

The benchmark runner does not execute generated commands. The above executions were manually reviewed and performed in a separate temporary fixture directory. Processor snapshots showed 100% CPU. Gemma and Mistral comparison models were downloading at time of writing; no results for them are claimed here.
