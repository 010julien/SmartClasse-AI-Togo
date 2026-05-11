# Quantization & Low-memory LLM setup

But: Gemma 4 large variants require a lot of RAM. Use one of these approaches:

1. Increase Docker Desktop memory

- Open Docker Desktop > Settings > Resources > Memory and increase to >=12GB.

2. Use a quantized local model with `llama-cpp-python` (recommended on constrained hosts)

Steps (high-level):

- Place a GGUF quantized model in `./models/`, for example:
  - `models/gemma-4-9b-q4.gguf`
  - Model providers: check licensing and download sources.

- Install `llama-cpp-python` in your Python environment. On Windows use conda:

```powershell
conda create -n sc-llm python=3.10 -y
conda activate sc-llm
pip install --upgrade pip
pip install llama-cpp-python
```

- Enable quantized mode by setting env var `USE_QUANTIZED_LLM=1` or editing `.env`:

```
USE_QUANTIZED_LLM=1
QUANTIZED_MODEL_PATH=models/gemma-4-9b-q4.gguf
```

- If running in Docker, ensure `./models` is mounted into the container. The project `docker-compose.yml` now mounts `./models:/app/models` and exposes `QUANTIZED_MODEL_PATH`.

- Restart the backend container:

```powershell
docker compose down
docker compose up --build -d
```

3. Fallback to Ollama

If quantized model is missing or `llama-cpp-python` fails to load, the code will automatically fall back to the Ollama client (if available). Check logs for messages mentioning `llama-cpp` or fallback.

Notes & caveats

- Quantized GGUF models can still be several GB. Confirm available disk and memory.
- GPU is helpful: `llama-cpp-python` can use `n_gpu_layers` and CUDA builds for acceleration.
- Licensing: ensure you have rights to download and use the model. Some GGUFs are community builds.

If you want, I can:

- Add an automated download helper (if you provide a URL and license), or
- Build a Dockerfile for a standalone `llama-cpp` serving container that the backend can call.
