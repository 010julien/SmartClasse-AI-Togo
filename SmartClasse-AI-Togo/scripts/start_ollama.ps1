Write-Host "== Start Ollama helper (PowerShell) =="

if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "ollama detected in PATH"
    Write-Host "Recommended: run the Ollama server/daemon per your installation. Example:"
    Write-Host "  ollama serve --host 127.0.0.1 --port 11434"
} else {
    Write-Host "ollama CLI not found. Install from https://ollama.com/docs"
    Write-Host "Or use the fallback scripts for LiteRT / llama.cpp in scripts\"
}

Write-Host "Ensure model is pulled (e.g. ollama pull gemma4:...) then restart backend"
