"""
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
wget https://huggingface.co/thewh1teagle/phonikud-tts-checkpoints/resolve/main/saspeech_automatic_stts2-light_epoch_00010.pth
wget https://github.com/thewh1teagle/StyleTTS2-lite branch: hebrew2
"""

"""
Script to create sample audio files for all WAV files in Demo/Audio directory
"""
import soundfile as sf
from pathlib import Path
from phonikud_onnx import Phonikud
import phonikud
from tts import TextToSpeech

phonikud_model = Phonikud('phonikud-1.0.int8.onnx')

default_text = """
ירושלים היא עיר עתיקה וחשובה במיוחד, שמכילה בתוכה שכבות רבות של היסטוריה, תרבות ורוחניות שנמשכות אלפי שנים, והיא מהווה מוקד מרכזי לשלושת הדתות הגדולות, יהדות, נצרות, ואסלאם. שמתחברות יחד במקום אחד ייחודי, מלא אנרגיה ומורכבות, שם אפשר למצוא אתרים קדושים, שכונות עתיקות ושווקים צבעוניים, וכל פינה מספרת סיפור של תקופות שונות, אנשים שונים ואירועים שהשפיעו על ההיסטוריה של העולם כולו, מה שהופך את ירושלים לא רק לעיר גאוגרפית, אלא גם למרכז של זהות, אמונה, וזיכרון קולקטיבי שממשיך לעורר השראה ולחבר בין אנשים מרקע שונה מכל קצוות תבל.
""".strip()

def phonemize(vocalized):
    phonemes = phonikud.phonemize(vocalized)
    return phonemes

def main():
    # Create samples directory
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)
    
    # Setup TTS model
    config_path = str(Path("StyleTTS2-lite") / "Configs" / "config.yaml")
    models_path = 'saspeech_automatic_stts2-light_epoch_00010.pth'
    tts = TextToSpeech(config_path, models_path)
    
    # Sample text to use for audio generation
    text = default_text
    vocalized = phonikud_model.add_diacritics(text)
    phonemes = phonemize(vocalized)
    
    # Parameters
    speed = 0.82
    denoise = 0.2
    avg_style = True
    stabilize = True
    
    # Use hardcoded reference audio file
    ref_audio_path = "StyleTTS2-lite/Demo/Audio/10_michael.wav"
    
    print(f"Processing reference audio: {ref_audio_path}")
    
    try:
        # Use the TTS synthesize method
        audio = tts.create(
            phonemes=phonemes,
            speaker_path=ref_audio_path,
            speed=speed,
            denoise=denoise,
            avg_style=avg_style,
            stabilize=stabilize,
            alpha=18
        )
        
        # Create output filename
        output_name = "sample_output.wav"
        output_path = samples_dir / output_name
        
        # Save audio
        sr = 24000
        sf.write(str(output_path), audio, sr)
        print(f"Created {output_name}")
        
    except Exception as e:
        print(f"Error processing {ref_audio_path}: {e}")
    
    print(f"\nSample created in {samples_dir} directory")


if __name__ == "__main__":
    main() 