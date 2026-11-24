#!/bin/sh
# Installs Aya for Linux and macOS (bash or zsh). Run from a checkout, or piped from curl.
# It never installs Ollama or models and never edits shell configuration.
set -eu

tarball=${AYA_TARBALL:-https://github.com/cadavidf/aya/archive/refs/heads/main.tar.gz}
bin_dir=${HOME}/.local/bin
target=${bin_dir}/aya
fail() { echo "Error: $1" >&2; exit 1; }

command -v python3 >/dev/null 2>&1 || fail "Python 3.8 or newer is required. macOS: brew install python (or https://www.python.org/downloads/). Debian/Ubuntu: sudo apt install python3. Fedora: sudo dnf install python3."
python3 -c 'import sys; sys.exit(sys.version_info < (3, 8))' || fail "Python 3.8 or newer is required; found $(python3 --version 2>&1)."

if [ -f "$0" ] && [ -f "$(dirname "$0")/aya.py" ]; then
    repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
else
    repo_dir=${XDG_DATA_HOME:-$HOME/.local/share}/aya
    command -v tar >/dev/null 2>&1 || fail "tar is required."
    tmp=$(mktemp -d) || fail "could not create a temporary directory."
    trap 'rm -rf "$tmp"' EXIT
    echo "Downloading Aya..."
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$tarball" -o "$tmp/aya.tar.gz" || fail "download failed: $tarball"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$tarball" -O "$tmp/aya.tar.gz" || fail "download failed: $tarball"
    else
        fail "curl or wget is required."
    fi
    mkdir "$tmp/src"
    tar -xzf "$tmp/aya.tar.gz" -C "$tmp/src" --strip-components=1 || fail "could not unpack the download."
    [ -f "$tmp/src/aya.py" ] || fail "the download does not contain aya.py."
    mkdir -p "$(dirname "$repo_dir")"
    rm -rf "$repo_dir"
    mv "$tmp/src" "$repo_dir"
fi

mkdir -p "$bin_dir"
if [ -L "$target" ] && [ "$(readlink "$target")" = "$repo_dir/bin/aya" ]; then
    :   # reinstall of our own launcher
elif [ -e "$target" ] || [ -L "$target" ]; then
    fail "${target} already exists and is not this Aya; remove it and rerun."
else
    ln -s "$repo_dir/bin/aya" "$target"
fi
chmod +x "$repo_dir/bin/aya"
echo "Installed ${target} (code in ${repo_dir})"

case ":$PATH:" in
    *":$bin_dir:"*) ;;
    *)  case ${SHELL:-} in */zsh) rc='~/.zshrc' ;; *) rc='~/.bashrc' ;; esac
        echo "Add ${bin_dir} to your PATH, then open a new terminal:"
        echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ${rc}" ;;
esac

if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama is not installed. Aya needs it: https://ollama.com/download"
    [ "$(uname -s)" = Linux ] && echo "  (Linux: curl -fsSL https://ollama.com/install.sh | sh)"
    echo "Then run: ollama pull dolphin3:latest"
elif ! ollama list 2>/dev/null | grep -q '^dolphin3:latest'; then
    echo "Ollama is installed, but the dolphin3:latest model was not found (or Ollama is not running)."
    echo "Start Ollama (open the app, or run: ollama serve), then run: ollama pull dolphin3:latest"
fi
echo "Start Aya with: aya"
