FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu

WORKDIR /app

RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         build-essential \
         cmake \
         gcc \
         g++ \
         git \
         python3-dev \
         libsndfile1-dev \
         libopenblas-dev \
         liblapack-dev \
         pkg-config \
         libffi-dev \
         libssl-dev \
         libespeak1 \
         libavformat-dev \
         libavcodec-dev \
         libavdevice-dev \
         libavutil-dev \
         libavfilter-dev \
         libswscale-dev \
         libswresample-dev \
         ffmpeg \
     && rm -rf /var/lib/apt/lists/*

# Support optional, lean requirements file via build-arg. Defaults to requirements.txt
ARG REQUIREMENTS=requirements.txt
# Copy both manifests so we can choose at build time without needing variable expansion in COPY
COPY requirements.txt requirements.ollama.txt ./
RUN pip install --no-cache-dir -r $REQUIREMENTS

COPY src ./src
COPY README.md LICENSE NOTICE.txt ./

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]