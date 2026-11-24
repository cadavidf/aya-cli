# Live command-generation evaluation — 2026-11-24

Model: local `dolphin3:latest`. These are small observations, not a statistical benchmark. All generated commands were reviewed before any execution.

| Task | Observation | Result |
| --- | --- | --- |
| Fabric: list patterns, before help context | Proposed `./fabric --list-templates`; executable path and flag were wrong. | Fail |
| Fabric: list patterns, with help context | Proposed `fabric -l`; listed 182 patterns. | Pass |
| Fabric: summarize text in dry-run mode, with help context | Omitted the requested pattern and dry-run; proposed options including wiping contexts or sessions. Rejected without execution. | Fail |
| FFmpeg: trim two seconds starting at one second, before help context | Used an invalid timestamp `00:00:001`; FFmpeg rejected it. | Fail |
| FFmpeg: extract MP3 to a filename with spaces, before help context | Produced valid audio but replaced the requested space in the filename. | Fail |
| FFmpeg: scale a 4:3 fixture to 160×120, before help context | Produced 160×120 video on that fixture. | Pass for fixture |
| FFmpeg: generate extraction for the real workout recording, with help context | Model generation did not finish after 123 seconds; no generated command was executed. A second attempt was interrupted after a prolonged wait. | Inconclusive; latency failure |

Manual reference artifacts were created separately from the user's recording: a 10.000-second WAV and a 10.009-second H.264/AAC clip from 60 seconds. These verify the media and FFmpeg workflow; they are not model-generated successes. The source was only read.

The model ran on CPU during the real-video test. Help context improved one Fabric task but did not make generated commands reliably correct or safe. Continue to require command approval and evaluate generated results independently.
