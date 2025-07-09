# phonikud-StyleTTS2-dockerized


## Setup

1. Install https://docs.astral.sh/uv/getting-started/installation
2. Run
```console
uv sync
uv run main.py
```

## Build image

```console
docker build --platform linux/amd64 -t phonikud-styletts2-app .
docker run phonikud-styletts2-app
```