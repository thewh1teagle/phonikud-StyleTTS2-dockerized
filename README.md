# phonikud-StyleTTS2-dockerized


## Prepare models

```console
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
wget https://huggingface.co/thewh1teagle/phonikud-tts-checkpoints/resolve/main/saspeech_automatic_stts2-light_epoch_00010.pth
```

## Setup without Docker

1. Install https://docs.astral.sh/uv/getting-started/installation
2. Run
```console
uv sync
uv run main.py
```

## Setup with Docker

```console
wget https://github.com/thewh1teagle/StyleTTS2-lite branch: hebrew2
docker build --platform linux/amd64 -t phonikud-styletts2-app .
docker run -p 7860:7860 phonikud-styletts2-app
```