#!/bin/sh
set -eu

# Install from a local checkout without changing shell configuration or models.
repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
bin_dir=${HOME}/.local/bin
target=${bin_dir}/aya
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required." >&2; exit 1; }
mkdir -p "$bin_dir"
if [ -e "$target" ] || [ -L "$target" ]; then
    echo "${target} already exists; leaving it unchanged." >&2
    exit 1
fi
ln -s "$repo_dir/bin/aya" "$target"
echo "Installed ${target}"
echo "Ensure ${bin_dir} is on PATH; install and start Ollama separately."
echo "Then pull a model: ollama pull dolphin3:latest"
