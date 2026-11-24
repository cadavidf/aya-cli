# Aya GPU experiment checkpoint

Updated: 2026-11-24. Machine: Intel iMac, AMD Radeon Pro 5500 XT, 8 GB VRAM. Aya still uses Ollama and Dolphin by default; this experiment does not change that configuration.

## Current evidence

- A separate llama.cpp build at `~/aya-gpu-lab/build-vulkan` uses Vulkan through MoltenVK, which ultimately uses Metal. It is not a separate macOS graphics driver. Source revision: `c212d25`.
- With GPU access outside the sandbox, device discovery reports `Vulkan0: AMD Radeon Pro 5500 XT`, 8176 MiB. The sandboxed process could not access Metal.
- One small float16 `ADD` GPU operation passed the test-backend-ops CPU comparison (1/1). This does not establish model correctness.
- A 361.8M-parameter SmolLM2 GGUF completed short `llama-bench` tests with one GPU layer and with `-ngl 99`. With 32 prompt tokens and 8 generated tokens, one repetition, the latter measured 395.17 prompt tokens/s and 46.22 generation tokens/s. The test disabled KV and operation offloading, so it does not mean all computation was on GPU. It does not test output correctness or represent Aya's model.
- Dolphin 8B Q4_K_M, with KV and operation offload disabled, completed the same short single-repetition benchmark: 1 layer, 5.96 prompt / 5.23 generation tokens/s; 8 layers, 6.88 / 5.17; 32 layers, 68.34 / 16.80. These are preliminary throughput figures, not output correctness or long-run stability measurements.
- Dolphin generated a sensible one-sentence explanation of FFmpeg with 32 GPU layers using llama-cli, 512 context, temperature 0 and 32 maximum tokens. The CLI reported 15.9 generation tokens/s. This one answer is only a smoke test.
- Aya's experimental llama-server adapter generated an FFmpeg explanation using the 32-layer Vulkan server at a reported 16.07 generation tokens/s. The temporary server was stopped after the test. The ChatML role delimiters match Ollama's template, but system-message and stop-setting parity has not been established.
- A 99-layer test was requested but interrupted before a result was returned. Its execution state is unknown. Earlier GPU resets and a system panic make stable operation a specific requirement, not an assumption.

## Stages

1. **Dolphin GPU smoke test.** Run 1 layer and short prompt/generation, then gradually increase layers. Confirm the reported device and memory use. Stop on an error, reset, freeze, or suspicious output; preserve the last working settings.
2. **Correctness.** Test small model-relevant matrix operations against the CPU, and compare deterministic model output for representative prompts. One passing ADD and a successful throughput benchmark are insufficient evidence.
3. **Reliability and speed.** Repeat short trials at the same context and layer settings, then test longer contexts while watching memory and system stability. Record model, quantization, backend, layer count, settings, repeat count and throughput. Never infer performance from a single run.
4. **Aya integration.** An opt-in local llama-server backend is implemented and passed one generation smoke test; Ollama remains the default. Validate model output and run Aya's command and media evaluations before relying on it.

## Reproduce GPU discovery and smoke test

These commands use installed local weights and do not download a model. GPU access requires an environment able to access Metal.

```sh
export VK_ICD_FILENAMES="$HOME/VulkanSDK/macOS/share/vulkan/icd.d/MoltenVK_icd.json"
"$HOME/aya-gpu-lab/build-vulkan/bin/llama-bench" --list-devices
"$HOME/aya-gpu-lab/build-vulkan/bin/llama-bench" \
  -m "$HOME/.ollama/models/blobs/sha256-1eee6953530837b2b17d61a4e6f71a5aa31c9714cfcf3cb141aa5c1972b5116b" \
  -dev Vulkan0 -ngl 1 -nkvo 1 -nopo 1 -p 32 -n 8 -r 1 -t 4 -o json
```

The working build required CMake 3.31.10 in `~/aya-gpu-lab/tools` and the Command Line Tools SDK C++ include path. Build artifacts are outside the Aya repository. A benchmark result alone does not prove generated text or commands are correct.

To start the tested experimental server in one terminal:

```sh
env VK_ICD_FILENAMES="$HOME/VulkanSDK/macOS/share/vulkan/icd.d/MoltenVK_icd.json" \
  "$HOME/aya-gpu-lab/build-vulkan/bin/llama-server" \
  -m "$HOME/.ollama/models/blobs/sha256-1eee6953530837b2b17d61a4e6f71a5aa31c9714cfcf3cb141aa5c1972b5116b" \
  -dev Vulkan0 -ngl 32 -nkvo --no-op-offload -c 2048 -np 1 \
  --host 127.0.0.1 --port 18631 --no-webui --chat-template chatml
```

In another terminal, run `AYA_BACKEND=llama AYA_LLAMA_URL=http://127.0.0.1:18631 aya`. Stop the server with Ctrl-C when finished. The server chooses the model; `AYA_MODEL` does not apply to this backend.
