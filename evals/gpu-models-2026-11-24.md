# GPU model smoke benchmarks — 2026-11-24

Intel iMac, Radeon Pro 5500 XT 8 GB, llama.cpp c212d25, Vulkan via MoltenVK. Existing local GGUF models; 32 GPU layers requested, KV and operation offload disabled, 32 prompt tokens, 8 generated tokens, 4 CPU threads, one repetition. Requested layers do not necessarily correspond to the same fraction of each model. Model sizes are approximate on-disk sizes; they are not measured GPU memory usage.

| Model | Size | Prompt tokens/s | Generation tokens/s |
| --- | ---: | ---: | ---: |
| Dolphin 3 8B Q4_K_M | 4.91 GB | 68.34 | 16.80 |
| Mistral 7B Instruct abliterated Q4_K_M | 4.37 GB | 68.18 | 16.59 |
| Gemma 3 4B abliterated Q4_K_M | 2.48 GB | 85.94 | 20.54 |
| Phi-4 Mini 3.8B Q4_K_M | 2.48 GB | 128.17 | 22.99 |
| Granite 3.3 8B Q4_K_M | 4.94 GB | 18.71 | 9.51 |

These are very short single-run throughput smoke tests, not accuracy, repeatability, long-context, memory-headroom, or stability results. All four new runs completed without process errors. Earlier CPU command tests found that Gemma produced invalid FFmpeg proposals and Mistral wrapped commands in backticks; see benchmark-2026-11-24.md. Do not infer model quality from speed.
