# Aya: local open-weight agent roadmap

## Objective

Run a less-restricted open-weight model reliably on this Intel iMac and improve Aya into a useful terminal agent. Measure actual behavior rather than assuming a model is capable. Preserve the `aya` command, camel, existing YouTube workflow, and approval before shell commands.

## Hardware and current evidence

- Intel Core i7, 40 GB system RAM; AMD Radeon Pro 5500 XT with 8 GB VRAM.
- Ollama 0.40.17 runs the installed `dolphin3:latest` on CPU. It loaded at approximately 5.6 GB in the observed run.
- GPU inference is not yet validated: macOS recorded repeated GPU resets and a WindowServer watchdog panic; one earlier GPU reset involved `llama-bench` on Metal. Model memory fit and backend stability are separate problems.
- A user-approved second Mac with Apple Silicon may be useful later, but is not currently accessible from this machine.

## Stage 1 — model compatibility and repeatable baseline

1. Download the explicitly less-restricted Gemma 3 4B and Mistral 7B GGUF candidates using Ollama; record exact model names, sizes, and provenance.
2. Run each sequentially with Aya's actual command prompt on the same Fabric listing, FFmpeg WAV extraction and FFmpeg trimming tasks. Record timeout, latency, and `ollama ps` processor/memory.
3. Review generated commands; run only safe, narrowly scoped candidates on synthetic fixtures in a separate temporary directory. Verify streams, filenames, durations and clip boundaries with ffprobe or media inspection. Do not treat text-only checks as proof of correctness.
4. Compare to installed Dolphin 3 using the same tasks. Repeat promising candidates and compare their stability before choosing a default. Keep Dolphin as default until the evidence supports changing it.

**Exit:** At least one candidate is loaded and responds on CPU, and the completed and failed tasks are documented with limitations. If downloads, availability, or CPU time prevent completion, record the precise blocker and resumable commands.

## Stage 2 — safe agent foundations

1. Improve Aya's conversational state, bounded prompts, visible progress, cancellation and explicit errors.
2. Evaluate project listing, searching, and reading in isolated directories, including a model trying to access outside the workspace.
3. Test a bounded model/tool loop on known projects and fail clearly if the model gives unsupported or ungrounded answers. Tool results are untrusted data.
4. Keep generated shell commands behind approval. Test displayed commands, paths with spaces and control characters.

**Exit:** Regression tests pass and reviewed live tasks show accurate, evidence-backed file answers and correct approval behavior.

## Stage 3 — editing and real tasks

1. Add reviewable file changes and test running, restricted to the intended workspace.
2. Evaluate a small coding fix and the user's Fabric and workout-video workflows using copies or separate output artifacts. Verify actual outputs and preserve user work.
3. Re-run previous evaluations and document failures before expanding autonomy.

**Exit:** Aya completes representative tasks without losing existing work, reports failures accurately, and the automated regression suite passes.

## Stage 4 — GPU investigation, separate from model choice

1. Review current upstream Intel/AMD backend fixes and identify a small, reversible change or an isolated Vulkan/Metal build. Do not replace the working Ollama installation.
2. Document rollback, memory use, exact source revision, CPU baseline and correctness tests before any GPU experiment.
3. Test deterministic output against CPU, then short workloads and stability. GPU reporting alone does not prove accuracy. Do not resume a risky GPU workload without the user understanding the existing reset history.

**Exit:** A candidate demonstrates correct output and stability on this specific Radeon GPU, or is documented as unproven and CPU remains the supported path.

## Stage checkpoints

At the end of each stage or meaningful session, update `CHECKPOINT.md` with Git commit, completed and pending tasks, exact test commands, observed results, and any limitations. Commit working changes. Keep results and model artifacts separate from the Git repository. Continue from that file after context compaction; do not infer that a model or backend passed without a recorded result.
