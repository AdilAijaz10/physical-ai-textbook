---
sidebar_position: 1
---

# Week 11: Voice Commands with OpenAI Whisper

## Learning Objectives

By the end of this week, you will be able to:
- Set up and configure OpenAI Whisper for speech recognition
- Integrate Whisper with ROS 2 for real-time voice command processing
- Implement natural language processing for command interpretation
- Create a voice command system for humanoid robot control
- Handle multiple speakers and noisy environments

## Introduction to OpenAI Whisper

OpenAI Whisper is a state-of-the-art speech recognition model that can transcribe speech to text with high accuracy. For humanoid robots, Whisper enables natural voice interaction, allowing users to control robots through spoken commands in various languages and accents.

### Key Features of Whisper
- **Multilingual Support**: Works with 99+ languages
- **Robust Performance**: Handles accents, background noise, and technical speech
- **Multiple Model Sizes**: From tiny (fast) to large (accurate)
- **Timestamp Support**: Provides word-level timing information
- **Speaker Diarization**: Can distinguish between different speakers

## Installing and Setting Up Whisper

### Prerequisites
- **Python**: 3.8 or higher
- **PyTorch**: 1.10 or higher
- **FFmpeg**: For audio processing
- **GPU**: CUDA-compatible GPU recommended for real-time performance

### Installation
```bash
# Install Whisper and dependencies
pip install openai-whisper
pip install torch torchvision torchaudio

# Install FFmpeg (Ubuntu/Debian)
sudo apt update
sudo apt install ffmpeg

# For ROS 2 integration
pip install rclpy
pip install speech-recognition
```

### Testing Installation
```python
# test_whisper.py - Test Whisper installation
import whisper

# Load model
model = whisper.load_model("base")  # or "small", "medium", "large"
print("Whisper model loaded successfully!")

# Test with a sample audio file
# result = model.transcribe("sample_audio.wav")
# print("Transcription:", result["text"])
```

## Basic Whisper Usage

### Transcribing Audio
```python
# basic_whisper_usage.py - Basic Whisper transcription
import whisper
import torch

def transcribe_audio(audio_path, model_size="base"):
    """Transcribe audio file using Whisper"""

    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load model
    model = whisper.load_model(model_size).to(device)

    # Transcribe
    result = model.transcribe(audio_path)

    return result["text"]

def transcribe_with_options(audio_path):
    """Transcribe with specific options"""
    model = whisper.load_model("base")

    # Transcribe with options
    result = model.transcribe(
        audio_path,
        language="en",  # Specify language
        temperature=0,  # Deterministic output
        best_of=5,      # Generate 5 candidates, pick best
        verbose=False   # Don't print progress
    )

    return result

# Example usage
if __name__ == "__main__":
    # This would transcribe an audio file
    # text = transcribe_audio("robot_commands.wav")
    # print(f"Transcribed text: {text}")
    pass
```

## Real-time Audio Processing

### Audio Input with PyAudio
```python
# real_time_audio.py - Real-time audio processing for Whisper
import pyaudio
import wave
import numpy as np
import threading
import queue
import whisper
import torch
import time

class RealTimeAudioProcessor:
    def __init__(self, model_size="base", chunk_size=1024, sample_rate=16000):
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.model_size = model_size

        # Audio parameters
        self.format = pyaudio.paInt16
        self.channels = 1
        self.record_seconds = 5  # Record in chunks

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Queues for processing
        self.audio_queue = queue.Queue()
        self.result_queue = queue.Queue()

        # Load Whisper model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_size).to(device)

        # Flags
        self.recording = False
        self.processing = False

    def start_recording(self):
        """Start recording audio"""
        self.recording = True

        # Open audio stream
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        # Start recording thread
        self.record_thread = threading.Thread(target=self.record_audio)
        self.record_thread.start()

        # Start processing thread
        self.process_thread = threading.Thread(target=self.process_audio)
        self.process_thread.start()

        print("Recording started...")

    def record_audio(self):
        """Record audio in chunks"""
        while self.recording:
            # Read audio data
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            self.audio_queue.put(data)

    def process_audio(self):
        """Process audio chunks with Whisper"""
        frames = []
        frame_count = 0

        while self.recording or not self.audio_queue.empty():
            try:
                # Get audio chunk
                chunk = self.audio_queue.get(timeout=0.1)
                frames.append(chunk)
                frame_count += 1

                # Process every N chunks
                if frame_count >= int(self.sample_rate * 2 / self.chunk_size):  # Process every 2 seconds
                    if len(frames) > 0:
                        # Convert frames to numpy array
                        audio_data = b''.join(frames)
                        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                        # Process with Whisper
                        self.process_with_whisper(audio_np)

                        # Clear frames
                        frames = []
                        frame_count = 0
            except queue.Empty:
                continue

    def process_with_whisper(self, audio_np):
        """Process audio with Whisper model"""
        if len(audio_np) == 0:
            return

        # Run transcription
        result = self.model.transcribe(audio_np, language="en")
        transcription = result["text"].strip()

        if transcription:  # Only add if there's actual text
            self.result_queue.put({
                "text": transcription,
                "timestamp": time.time()
            })
            print(f"Transcription: {transcription}")

    def stop_recording(self):
        """Stop recording and processing"""
        self.recording = False

        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()

        if hasattr(self, 'record_thread'):
            self.record_thread.join()

        if hasattr(self, 'process_thread'):
            self.process_thread.join()

        self.audio.terminate()
        print("Recording stopped.")

# Example usage
if __name__ == "__main__":
    processor = RealTimeAudioProcessor()
    try:
        processor.start_recording()
        time.sleep(10)  # Record for 10 seconds
        processor.stop_recording()
    except KeyboardInterrupt:
        processor.stop_recording()
```

## ROS 2 Integration

### Whisper ROS 2 Node
```python
# whisper_ros_node.py - ROS 2 node for Whisper integration
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import AudioData
from geometry_msgs.msg import Twist
import whisper
import torch
import numpy as np
import threading
import queue
import time

class WhisperROSNode(Node):
    def __init__(self):
        super().__init__('whisper_ros_node')

        # Initialize Whisper model
        self.model_size = self.declare_parameter('model_size', 'base').value
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(self.model_size).to(device)

        # Publishers
        self.command_pub = self.create_publisher(String, 'voice_commands', 10)
        self.text_pub = self.create_publisher(String, 'transcribed_text', 10)

        # Subscribers
        self.audio_sub = self.create_subscription(
            AudioData, 'audio_input', self.audio_callback, 10
        )

        # Service for manual transcription
        self.transcribe_service = self.create_service(
            Trigger, 'transcribe_audio', self.transcribe_service_callback
        )

        # Parameters
        self.silence_threshold = self.declare_parameter('silence_threshold', 0.01).value
        self.min_audio_duration = self.declare_parameter('min_audio_duration', 1.0).value

        # Audio processing
        self.audio_buffer = []
        self.processing_lock = threading.Lock()

        # Timer for processing audio
        self.process_timer = self.create_timer(2.0, self.process_audio_buffer)

        self.get_logger().info('Whisper ROS Node initialized')

    def audio_callback(self, msg):
        """Handle incoming audio data"""
        # Convert audio data to numpy array
        audio_data = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32) / 32768.0

        # Check if audio has sufficient energy (not silence)
        if np.mean(np.abs(audio_data)) > self.silence_threshold:
            with self.processing_lock:
                self.audio_buffer.extend(audio_data)

    def process_audio_buffer(self):
        """Process accumulated audio buffer"""
        with self.processing_lock:
            if len(self.audio_buffer) == 0:
                return

            # Convert to numpy array
            audio_np = np.array(self.audio_buffer)

            # Check if buffer has minimum required duration
            duration = len(audio_np) / 16000.0  # Assuming 16kHz sample rate
            if duration < self.min_audio_duration:
                return

            # Clear buffer for next processing
            self.audio_buffer = []

        # Process with Whisper in a separate thread to avoid blocking
        processing_thread = threading.Thread(
            target=self.transcribe_audio,
            args=(audio_np,)
        )
        processing_thread.start()

    def transcribe_audio(self, audio_np):
        """Transcribe audio using Whisper"""
        try:
            # Transcribe audio
            result = self.model.transcribe(audio_np, language="en")
            text = result["text"].strip()

            if text:
                # Publish transcribed text
                text_msg = String()
                text_msg.data = text
                self.text_pub.publish(text_msg)

                # Parse command and publish if valid
                command = self.parse_command(text)
                if command:
                    cmd_msg = String()
                    cmd_msg.data = command
                    self.command_pub.publish(cmd_msg)
                    self.get_logger().info(f'Voice command: {command}')

        except Exception as e:
            self.get_logger().error(f'Error in transcription: {e}')

    def parse_command(self, text):
        """Parse natural language command"""
        # Convert to lowercase for easier matching
        text_lower = text.lower()

        # Define command patterns
        command_patterns = {
            'move_forward': ['forward', 'go forward', 'move forward', 'walk forward'],
            'move_backward': ['backward', 'go backward', 'move backward', 'walk backward'],
            'turn_left': ['turn left', 'left', 'rotate left'],
            'turn_right': ['turn right', 'right', 'rotate right'],
            'stop': ['stop', 'halt', 'freeze', 'stand still'],
            'wave': ['wave', 'wave hello', 'hello'],
            'dance': ['dance', 'do a dance'],
            'sit': ['sit', 'sit down'],
            'stand': ['stand', 'stand up']
        }

        # Check for command matches
        for command, patterns in command_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return command

        # If no specific command found, return the text as a general command
        if len(text) > 3:  # At least 3 characters
            return f"GENERAL_COMMAND: {text}"

        return None

    def transcribe_service_callback(self, request, response):
        """Service callback for manual transcription"""
        # This would trigger transcription of currently buffered audio
        # For now, we'll just return a placeholder
        response.success = True
        response.message = "Transcription service called"
        return response

def main(args=None):
    rclpy.init(args=args)
    whisper_node = WhisperROSNode()

    try:
        rclpy.spin(whisper_node)
    except KeyboardInterrupt:
        pass
    finally:
        whisper_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Voice Command Processing Pipeline

### Command Interpretation System
```python
# command_interpreter.py - Voice command interpretation system
import re
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
import spacy  # For NLP processing

@dataclass
class Command:
    action: str
    parameters: Dict[str, any]
    confidence: float
    raw_text: str

class VoiceCommandInterpreter:
    def __init__(self):
        # Load NLP model (install with: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("SpaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None

        # Define command patterns
        self.command_patterns = {
            # Movement commands
            'move': {
                'patterns': [
                    r'go (?P<direction>forward|backward|left|right)',
                    r'move (?P<direction>forward|backward|left|right)',
                    r'walk (?P<direction>forward|backward|left|right)',
                    r'go (?P<distance>\d+(?:\.\d+)?) (?:meters|steps)',
                ],
                'action': 'move'
            },
            # Navigation commands
            'navigate': {
                'patterns': [
                    r'go to (?P<location>[\w\s]+)',
                    r'navigate to (?P<location>[\w\s]+)',
                    r'move to (?P<location>[\w\s]+)',
                ],
                'action': 'navigate'
            },
            # Manipulation commands
            'manipulate': {
                'patterns': [
                    r'pick up (?P<object>[\w\s]+)',
                    r'grab (?P<object>[\w\s]+)',
                    r'lift (?P<object>[\w\s]+)',
                    r'put down (?P<object>[\w\s]+)',
                    r'drop (?P<object>[\w\s]+)',
                ],
                'action': 'manipulate'
            },
            # Interaction commands
            'interact': {
                'patterns': [
                    r'wave',
                    r'say hello',
                    r'greet',
                    r'dance',
                    r'sit',
                    r'stand',
                    r'wave to (?P<target>[\w\s]+)',
                ],
                'action': 'interact'
            }
        }

        # Location keywords
        self.locations = {
            'kitchen', 'living room', 'bedroom', 'bathroom', 'office',
            'dining room', 'hallway', 'garage', 'garden', 'entrance'
        }

        # Object keywords
        self.objects = {
            'cup', 'bottle', 'book', 'phone', 'keys', 'ball',
            'box', 'toy', 'food', 'water', 'apple', 'banana'
        }

    def interpret(self, text: str) -> Optional[Command]:
        """Interpret voice command and return structured command"""
        if not text.strip():
            return None

        # Clean text
        text = text.strip().lower()

        # Try to match command patterns
        for cmd_type, config in self.command_patterns.items():
            for pattern in config['patterns']:
                match = re.search(pattern, text)
                if match:
                    parameters = match.groupdict()

                    # Extract additional information using NLP if available
                    if self.nlp:
                        doc = self.nlp(text)
                        # Extract entities, dependencies, etc.
                        for ent in doc.ents:
                            if ent.label_ in ['PERSON', 'GPE', 'ORG', 'MONEY', 'QUANTITY']:
                                parameters[ent.label_.lower()] = ent.text

                    # Calculate confidence based on pattern match quality
                    confidence = self.calculate_confidence(text, match)

                    return Command(
                        action=config['action'],
                        parameters=parameters,
                        confidence=confidence,
                        raw_text=text
                    )

        # If no pattern matched, try semantic analysis
        return self.semantic_analysis(text)

    def calculate_confidence(self, text: str, match) -> float:
        """Calculate confidence score for the match"""
        # Base confidence from pattern match
        base_confidence = 0.8

        # Adjust based on text length and match completeness
        match_length = len(match.group(0))
        text_length = len(text)

        # Longer, more specific matches get higher confidence
        length_factor = min(1.0, match_length / text_length)

        return base_confidence * (0.5 + 0.5 * length_factor)

    def semantic_analysis(self, text: str) -> Optional[Command]:
        """Perform semantic analysis when pattern matching fails"""
        # Simple keyword-based approach
        doc = self.nlp(text) if self.nlp else None

        # Identify action words
        action_words = ['go', 'move', 'walk', 'navigate', 'pick', 'grab', 'wave', 'sit', 'stand', 'dance']

        for word in action_words:
            if word in text:
                # Determine the most likely action based on context
                if any(loc in text for loc in self.locations):
                    return Command(
                        action='navigate',
                        parameters={'location': self.extract_location(text)},
                        confidence=0.6,
                        raw_text=text
                    )
                elif any(obj in text for obj in self.objects):
                    return Command(
                        action='manipulate',
                        parameters={'object': self.extract_object(text)},
                        confidence=0.6,
                        raw_text=text
                    )
                else:
                    return Command(
                        action='interact',
                        parameters={'action': word},
                        confidence=0.5,
                        raw_text=text
                    )

        # If no clear action, return as general command
        return Command(
            action='general',
            parameters={'text': text},
            confidence=0.3,
            raw_text=text
        )

    def extract_location(self, text: str) -> str:
        """Extract location from text"""
        for loc in self.locations:
            if loc in text:
                return loc
        return 'unknown'

    def extract_object(self, text: str) -> str:
        """Extract object from text"""
        for obj in self.objects:
            if obj in text:
                return obj
        return 'unknown'

# Example usage
if __name__ == "__main__":
    interpreter = VoiceCommandInterpreter()

    test_commands = [
        "Go forward 2 meters",
        "Navigate to the kitchen",
        "Pick up the red cup",
        "Wave to the person",
        "Turn left and go straight"
    ]

    for cmd in test_commands:
        result = interpreter.interpret(cmd)
        if result:
            print(f"Input: {cmd}")
            print(f"Action: {result.action}")
            print(f"Parameters: {result.parameters}")
            print(f"Confidence: {result.confidence:.2f}")
            print("---")
```

## Advanced Voice Processing

### Speaker Diarization and Noise Reduction
```python
# advanced_voice_processing.py - Advanced voice processing features
import numpy as np
from scipy import signal
import librosa
import webrtcvad  # For voice activity detection

class AdvancedVoiceProcessor:
    def __init__(self):
        # Initialize VAD (Voice Activity Detection)
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)  # Aggressive mode

        # Audio processing parameters
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)

        # Noise reduction parameters
        self.noise_threshold = 0.01
        self.speech_threshold = 0.05

    def preprocess_audio(self, audio_data):
        """Preprocess audio for better Whisper performance"""
        # Convert to float32 if needed
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Normalize audio
        audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data

        # Apply noise reduction
        audio_data = self.reduce_noise(audio_data)

        # Apply pre-emphasis filter
        audio_data = self.pre_emphasis_filter(audio_data)

        return audio_data

    def reduce_noise(self, audio_data):
        """Simple noise reduction using spectral gating"""
        # Compute STFT
        stft = librosa.stft(audio_data)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # Estimate noise profile (first 0.5 seconds)
        noise_profile = np.mean(magnitude[:, :int(0.5 * self.sample_rate / 512)], axis=1)

        # Apply spectral gating
        enhanced_magnitude = np.maximum(magnitude - noise_profile[:, np.newaxis] * 0.3, 0)

        # Reconstruct signal
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft)

        return enhanced_audio

    def pre_emphasis_filter(self, audio_data, coeff=0.97):
        """Apply pre-emphasis filter"""
        return np.append(audio_data[0], audio_data[1:] - coeff * audio_data[:-1])

    def detect_voice_activity(self, audio_data):
        """Detect voice activity in audio"""
        # Convert to 16-bit PCM
        audio_pcm = (audio_data * 32767).astype(np.int16)

        # Split into frames
        frames = self.frame_audio(audio_pcm)

        # Check each frame for voice activity
        vad_results = []
        for frame in frames:
            if len(frame) == self.frame_size:
                is_speech = self.vad.is_speech(frame.tobytes(), self.sample_rate)
                vad_results.append(is_speech)

        return vad_results

    def frame_audio(self, audio_data):
        """Split audio into frames for VAD"""
        frames = []
        for i in range(0, len(audio_data) - self.frame_size, self.frame_size):
            frame = audio_data[i:i + self.frame_size]
            frames.append(frame)
        return frames

    def segment_speech(self, audio_data, min_silence_duration=0.5):
        """Segment speech from continuous audio"""
        vad_results = self.detect_voice_activity(audio_data)

        # Convert frame-level VAD to time segments
        speech_segments = []
        in_speech = False
        start_time = 0

        frame_duration = self.frame_duration / 1000.0  # Convert to seconds

        for i, is_speech in enumerate(vad_results):
            current_time = i * frame_duration

            if is_speech and not in_speech:
                # Start of speech segment
                start_time = current_time
                in_speech = True
            elif not is_speech and in_speech:
                # End of speech segment
                if current_time - start_time >= 0.2:  # Minimum speech duration
                    speech_segments.append((start_time, current_time))
                in_speech = False

        # Handle case where audio ends in speech
        if in_speech:
            if len(audio_data) / self.sample_rate - start_time >= 0.2:
                speech_segments.append((start_time, len(audio_data) / self.sample_rate))

        return speech_segments

# Integration with Whisper node
class EnhancedWhisperNode(WhisperROSNode):
    def __init__(self):
        super().__init__()

        # Initialize advanced processor
        self.advanced_processor = AdvancedVoiceProcessor()

        # Add publisher for voice activity
        self.vad_pub = self.create_publisher(Bool, 'voice_activity', 10)

    def audio_callback(self, msg):
        """Enhanced audio callback with preprocessing"""
        # Convert audio data
        audio_data = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32) / 32768.0

        # Preprocess audio
        processed_audio = self.advanced_processor.preprocess_audio(audio_data)

        # Detect voice activity
        vad_results = self.advanced_processor.detect_voice_activity(processed_audio)
        has_voice = any(vad_results)

        # Publish voice activity
        vad_msg = Bool()
        vad_msg.data = has_voice
        self.vad_pub.publish(vad_msg)

        # Only add to buffer if voice detected
        if has_voice and np.mean(np.abs(processed_audio)) > self.silence_threshold:
            with self.processing_lock:
                self.audio_buffer.extend(processed_audio)
```

## Practical Exercise

### Exercise 1: Basic Whisper Setup
1. Install OpenAI Whisper and dependencies
2. Test transcription with sample audio files
3. Experiment with different model sizes
4. Evaluate transcription accuracy

### Exercise 2: Real-time Audio Processing
1. Set up PyAudio for real-time recording
2. Implement audio buffering and processing
3. Integrate Whisper with real-time audio
4. Test with live microphone input

### Exercise 3: ROS 2 Integration
1. Create a ROS 2 node for Whisper
2. Subscribe to audio input topics
3. Publish transcribed text and commands
4. Test voice command interpretation

## Advanced Topics

### Multiple Speaker Handling
```python
# multi_speaker_handling.py - Handling multiple speakers
import pyaudio
import numpy as np
from sklearn.cluster import KMeans
import webrtcvad

class MultiSpeakerProcessor:
    def __init__(self, num_speakers=2):
        self.num_speakers = num_speakers
        self.vad = webrtcvad.Vad(2)  # Medium sensitivity

        # Audio parameters
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)

        # Speaker models
        self.speaker_models = [None] * num_speakers
        self.speaker_assignments = {}

    def separate_speakers(self, audio_data):
        """Separate audio by speaker using simple energy-based approach"""
        # This is a simplified approach
        # For real applications, use more sophisticated methods like:
        # - Speaker embedding extraction (e.g., with Pyannote.audio)
        # - Speech separation models
        # - Direction of arrival estimation (with microphone arrays)

        # For now, we'll use a simple approach
        frames = self.frame_audio(audio_data)
        speaker_labels = []

        for frame in frames:
            if len(frame) == self.frame_size:
                is_speech = self.vad.is_speech(frame.tobytes(), self.sample_rate)
                if is_speech:
                    # Simple round-robin assignment for demonstration
                    speaker_id = len(speaker_labels) % self.num_speakers
                    speaker_labels.append(speaker_id)
                else:
                    speaker_labels.append(-1)  # No speaker

        return speaker_labels

    def frame_audio(self, audio_data):
        """Split audio into frames"""
        frames = []
        for i in range(0, len(audio_data) - self.frame_size, self.frame_size):
            frame = audio_data[i:i + self.frame_size]
            frames.append(frame)
        return frames
```

### Context-Aware Command Processing
```python
# context_aware_processing.py - Context-aware command processing
class ContextAwareInterpreter(VoiceCommandInterpreter):
    def __init__(self):
        super().__init__()

        # Context variables
        self.robot_location = "unknown"
        self.robot_state = "idle"
        self.last_command_time = 0
        self.command_history = []

    def interpret_with_context(self, text: str) -> Optional[Command]:
        """Interpret command with context awareness"""
        command = self.interpret(text)

        if command:
            # Enhance command with context
            command.parameters['context'] = {
                'robot_location': self.robot_location,
                'robot_state': self.robot_state,
                'timestamp': time.time()
            }

            # Add to history
            self.command_history.append(command)

            # Update context based on command
            self.update_context(command)

        return command

    def update_context(self, command: Command):
        """Update context based on executed command"""
        if command.action == 'navigate':
            if 'location' in command.parameters:
                self.robot_location = command.parameters['location']

        self.last_command_time = time.time()
        self.robot_state = 'executing' if command else 'idle'
```

## Summary

This week covered voice commands with OpenAI Whisper:
- Whisper installation and basic usage
- Real-time audio processing and buffering
- ROS 2 integration for voice command systems
- Natural language processing for command interpretation
- Advanced audio preprocessing and noise reduction
- Multiple speaker handling and context awareness

## Next Week Preview

Week 12 will focus on LLM cognitive planning, where you'll learn to integrate large language models for high-level task planning and reasoning in humanoid robots.