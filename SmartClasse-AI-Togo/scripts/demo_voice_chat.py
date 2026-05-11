"""Demo: voice -> LINGUIX chat -> save TTS audio

Usage:
    python scripts/demo_voice_chat.py --file samples/sample.wav --host http://127.0.0.1:8010

The script posts a WAV file to `/agents/linguix/chat` (multipart) and saves the returned
assistant audio (if present) to `data/audio/`.
"""
import argparse
import os
import requests


def _unwrap_payload(payload):
    """Unwrap nested API envelopes like {status, result: {status, result: ...}}."""
    current = payload
    for _ in range(5):
        if not isinstance(current, dict):
            return current
        if "result" in current and isinstance(current["result"], dict):
            current = current["result"]
            continue
        return current
    return current


def run_demo(file_path: str, host: str = "http://127.0.0.1:8010") -> None:
    url = f"{host}/agents/linguix/chat"
    files = {"file": open(file_path, "rb")}
    data = {"language": "french", "speak": "true", "user_id": "demo_user", "user_name": "Demo"}

    print(f"Sending {file_path} to {url} ...")
    resp = requests.post(url, files=files, data=data, timeout=60)
    files["file"].close()

    if resp.status_code != 200:
        print("Request failed:", resp.status_code, resp.text)
        return

    j = resp.json()
    print("Response:", j.get("status"))
    result = _unwrap_payload(j.get("result") or j.get("pipeline") or j)

    # Try to extract audio path/url
    audio = None
    if isinstance(result, dict):
        audio = result.get("audio") or result.get("audio_path") or result.get("audio_url")
    if audio is None and isinstance(j.get("result"), dict):
        unwrapped = _unwrap_payload(j.get("result"))
        if isinstance(unwrapped, dict):
            audio = unwrapped.get("audio") or unwrapped.get("audio_path") or unwrapped.get("audio_url")

    # If we have an audio file path, attempt to save it
    if isinstance(audio, dict):
        audio_path = audio.get("audio_path")
        if audio_path and os.path.exists(audio_path):
            dest = os.path.join("data", "audio", os.path.basename(audio_path))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(audio_path, "rb") as src, open(dest, "wb") as dst:
                dst.write(src.read())
            print("Saved audio to", dest)
        else:
            print("Audio meta present but no file path returned.", audio)
    elif isinstance(audio, str) and audio.startswith("/audio/"):
        # Try to download via static route
        audio_url = f"{host}{audio}"
        r2 = requests.get(audio_url, timeout=30)
        if r2.status_code == 200:
            dest = os.path.join("data", "audio", os.path.basename(audio))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(r2.content)
            print("Downloaded audio to", dest)
        else:
            print("Failed to download audio via static route", audio_url)
    else:
        # Print a concise hint to debug non-speech/no-audio responses.
        if isinstance(result, dict) and result.get("status") == "no_speech":
            print("No speech detected in sample audio.")
        else:
            print("No audio returned by the API.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to WAV/MP3 to send")
    parser.add_argument("--host", default="http://127.0.0.1:8010", help="Backend host URL")
    args = parser.parse_args()
    run_demo(args.file, args.host)
