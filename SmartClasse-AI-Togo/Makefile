# Makefile — Quick Commands for SmartClasse AI Development

.PHONY: help setup install test run clean demo gemma lint format

help:
	@echo "SmartClasse AI — Development Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          — Full setup (venv + deps + gemma4)"
	@echo "  make install        — Install dependencies only"
	@echo "  make gemma          — Download Gemma 4 E4B via Ollama"
	@echo ""
	@echo "Development:"
	@echo "  make run            — Start FastAPI server (port 8000)"
	@echo "  make ollama         — Start Ollama server (background)"
	@echo "  make test           — Run pytest tests"
	@echo "  make lint           — Lint code with flake8"
	@echo "  make format         — Format code with black"
	@echo ""
	@echo "Testing:"
	@echo "  make adaptix-test   — Test ADAPTIX agent"
	@echo "  make linguix-test   — Test LINGUIX agent"
	@echo ""
	@echo "Deployment:"
	@echo "  make clean          — Clean cache & build files"
	@echo "  make demo           — Build demo for Hugging Face Spaces"

setup:
	@echo "🚀 Starting full setup..."
	python -m venv venv
	./venv/Scripts/activate && pip install --upgrade pip
	./venv/Scripts/activate && pip install -r requirements.txt
	@echo "✅ Setup complete. Run 'make gemma' next"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

gemma:
	@echo "📥 Downloading Gemma 4 E4B (3.9 GB)..."
	ollama pull gemma4:e4b
	@echo "✅ Gemma 4 downloaded. Run 'make ollama' to start server"

ollama:
	@echo "🔧 Starting Ollama server..."
	ollama serve

run:
	@echo "🚀 Starting FastAPI server..."
	uvicorn src.main:app --reload --port 8000

test:
	@echo "🧪 Running tests..."
	pytest -v tests/

adaptix-test:
	@echo "🧪 Testing ADAPTIX agent..."
	curl -X POST http://localhost:8000/agents/adaptix/generate \
	  -H "Content-Type: application/json" \
	  -d '{"student_name":"Kossi","level":"CM1","subject":"math","topic":"fractions","language":"kabyie"}'

linguix-test:
	@echo "🧪 Testing LINGUIX agent..."
	curl -X POST http://localhost:8000/agents/linguix/translate_instruction \
	  -H "Content-Type: application/json" \
	  -d '{"instruction":"Calculez le quart de 48","source_language":"french","target_languages":["kabyie"],"audio_output":false}'

lint:
	@echo "🔍 Linting code..."
	flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

format:
	@echo "🎨 Formatting code with Black..."
	black src/

clean:
	@echo "🧹 Cleaning cache & build files..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.coverage' -delete
	find . -type d -name 'dist' -delete
	find . -type d -name 'build' -delete
	find . -type d -name '*.egg-info' -delete
	@echo "✅ Clean complete"

demo:
	@echo "🎬 Preparing demo for Hugging Face Spaces..."
	@echo "TODO: Create demo files"
