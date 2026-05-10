#!/usr/bin/env bash
set -euo pipefail

echo "== Start fallback: llama.cpp / LiteRT helper =="

MODEL_DIR="models"
MODEL_FILE="<place-your-model.bin-or-ggml-file-here>"

if [ ! -d "$MODEL_DIR" ]; then
  echo "Create $MODEL_DIR and place your optimized model file (ggml or lite format) there."
fi

echo "Example commands (adjust paths and binary names):"
echo "- llama.cpp (native):"
echo "  ./main -m $MODEL_DIR/$MODEL_FILE -p 'Hello'"
echo "- LiteRT (example using litert runner):"
echo "  litert --model $MODEL_DIR/$MODEL_FILE --port 11434"

echo "These are templates — consult llama.cpp / LiteRT docs for exact flags."
