#!/usr/bin/env bash
set -euo pipefail

echo "== Start Ollama helper script =="

if command -v ollama >/dev/null 2>&1; then
  echo "ollama found in PATH"
  echo "You can start the Ollama service according to your install. Typical commands (example):"
  echo "  ollama serve --host 127.0.0.1 --port 11434"
  echo "Or run the daemon documented by your Ollama release."
else
  echo "ollama CLI not found. Please install Ollama: https://ollama.com/docs"
  echo "If you cannot run Ollama, use the fallback scripts for LiteRT / llama.cpp in scripts/"
fi

echo "Ensure your model gemma4 is available (ollama pull <model>), then restart the backend."
