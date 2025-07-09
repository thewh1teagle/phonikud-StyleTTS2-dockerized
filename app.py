from flask import Flask, render_template, request, jsonify, send_file
from flask_restx import Api, Resource, fields
from pathlib import Path
import soundfile as sf
from phonikud_onnx import Phonikud
import phonikud
from tts import TextToSpeech
import os

app = Flask(__name__)

# Configure Flask-RESTX
api = Api(
    app,
    version='1.0',
    title='StyleTTS2 Hebrew TTS API',
    description='Hebrew Text-to-Speech API using StyleTTS2 and Phonikud',
    doc='/api/',
    prefix='/api'
)

# Initialize models
phonikud_model = Phonikud('phonikud-1.0.int8.onnx')

# Setup TTS model
config_path = str(Path("StyleTTS2-lite") / "Configs" / "config.yaml")
models_path = 'saspeech_automatic_stts2-light_epoch_00010.pth'
tts = TextToSpeech(config_path, models_path)

# Create samples directory
samples_dir = Path("samples")
samples_dir.mkdir(exist_ok=True)

# API Models
generate_model = api.model('GenerateRequest', {
    'text': fields.String(required=True, description='The input text'),
    'type': fields.String(required=False, description='Input type: phonemes, unvocalized, or vocalized (default: unvocalized)', 
                         enum=['phonemes', 'unvocalized', 'vocalized'], default='unvocalized'),
    'ref_audio': fields.String(required=False, description='Reference audio filename (default: 10_michael.wav)', default='10_michael.wav')
})

generate_response = api.model('GenerateResponse', {
    'success': fields.Boolean(description='Whether generation was successful'),
    'filename': fields.String(description='Generated audio filename'),
    'phonemes': fields.String(description='Generated phonemes'),
    'vocalized_text': fields.String(description='Vocalized Hebrew text (if applicable)')
})

error_response = api.model('ErrorResponse', {
    'error': fields.String(description='Error message')
})

def get_reference_audio_files():
    """Get all WAV files from StyleTTS2-lite/Demo/Audio/"""
    audio_dir = Path("StyleTTS2-lite/Demo/Audio")
    if audio_dir.exists():
        return sorted([f.name for f in audio_dir.glob("*.wav")])
    return []

def phonemize_text(text):
    """Convert text to phonemes"""
    vocalized = phonikud_model.add_diacritics(text)
    phonemes = phonikud.phonemize(vocalized)
    return phonemes

def vocalize_and_phonemize(text):
    """Vocalize text and convert to phonemes"""
    vocalized = phonikud_model.add_diacritics(text)
    phonemes = phonikud.phonemize(vocalized)
    return phonemes

@app.route('/')
def index():
    """Serve the main page"""
    audio_files = get_reference_audio_files()
    return render_template('index.html', audio_files=audio_files)

# API namespace
ns = api.namespace('tts', description='Text-to-Speech operations')

@ns.route('/generate')
class GenerateAudio(Resource):
    @api.expect(generate_model)
    @api.marshal_with(generate_response, code=200)
    @api.marshal_with(error_response, code=400)
    @api.marshal_with(error_response, code=500)
    def post(self):
        """Generate audio from text input"""
        try:
            data = request.json
            if not data:
                return {'error': 'No JSON data provided'}, 400
                
            input_text = data.get('text', '').strip()
            input_type = data.get('type', 'unvocalized')
            ref_audio = data.get('ref_audio', '10_michael.wav')
            
            if not input_text:
                return {'error': 'Text input is required'}, 400
            
            if not ref_audio:
                return {'error': 'Reference audio file is required'}, 400
            
            # Process input based on type
            vocalized_text = None
            if input_type == 'phonemes':
                phonemes = input_text
            elif input_type == 'unvocalized':
                vocalized_text = phonikud_model.add_diacritics(input_text)
                phonemes = phonikud.phonemize(vocalized_text)
            else:  # vocalized
                vocalized_text = input_text
                phonemes = phonikud.phonemize(input_text)
            
            # Reference audio path
            ref_audio_path = str(Path("StyleTTS2-lite/Demo/Audio") / ref_audio)
            
            # Generate audio
            audio = tts.create(
                phonemes=phonemes,
                speaker_path=ref_audio_path,
                speed=0.82,
                denoise=0.2,
                avg_style=True,
                stabilize=True,
                alpha=18
            )
            
            # Save audio
            output_filename = f"output_{input_type}.wav"
            output_path = samples_dir / output_filename
            sr = 24000
            sf.write(str(output_path), audio, sr)
            
            return {
                'success': True,
                'filename': output_filename,
                'phonemes': phonemes,
                'vocalized_text': vocalized_text
            }
            
        except Exception as e:
            return {'error': str(e)}, 500

@ns.route('/voices')
class GetVoices(Resource):
    @api.marshal_with(api.model('VoicesResponse', {
        'voices': fields.List(fields.String, description='Available voice files')
    }))
    def get(self):
        """Get list of available reference voices"""
        voices = get_reference_audio_files()
        return {'voices': voices}

# Keep the original route for the web interface
@app.route('/generate', methods=['POST'])
def generate_audio_web():
    """Generate audio based on input type (for web interface)"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        input_text = data.get('text', '').strip()
        input_type = data.get('type', 'vocalized')
        ref_audio = data.get('ref_audio', '')
        
        if not input_text:
            return jsonify({'error': 'Text input is required'}), 400
        
        if not ref_audio:
            return jsonify({'error': 'Reference audio file is required'}), 400
        
        # Process input based on type
        vocalized_text = None
        if input_type == 'phonemes':
            phonemes = input_text
        elif input_type == 'unvocalized':
            vocalized_text = phonikud_model.add_diacritics(input_text)
            phonemes = phonikud.phonemize(vocalized_text)
        else:  # vocalized
            vocalized_text = input_text
            phonemes = phonikud.phonemize(input_text)
        
        # Reference audio path
        ref_audio_path = str(Path("StyleTTS2-lite/Demo/Audio") / ref_audio)
        
        # Generate audio
        audio = tts.create(
            phonemes=phonemes,
            speaker_path=ref_audio_path,
            speed=0.82,
            denoise=0.2,
            avg_style=True,
            stabilize=True,
            alpha=18
        )
        
        # Save audio
        output_filename = f"output_{input_type}.wav"
        output_path = samples_dir / output_filename
        sr = 24000
        sf.write(str(output_path), audio, sr)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'phonemes': phonemes,
            'vocalized_text': vocalized_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio file for playback"""
    file_path = samples_dir / filename
    if file_path.exists():
        return send_file(file_path, mimetype='audio/wav')
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True) 