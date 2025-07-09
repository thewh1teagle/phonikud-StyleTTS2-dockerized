# phonikud-StyleTTS2-dockerized


## Setup without Docker

1. Install https://docs.astral.sh/uv/getting-started/installation
2. Run
```console
uv sync
uv run main.py
```

## Setup with Docker

```console
docker build --platform linux/amd64 -t phonikud-styletts2-app .
docker run -p 7860:7860 phonikud-styletts2-app
```