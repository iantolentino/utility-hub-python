**Real-time subtitle / captioning overlay**

Lightweight, modular Python app that records microphone audio, uses Voice Activity Detection (VAD) to find speech, sends speech segments to a worker pool for speech-to-text (default backend: VOSK), and displays captions in an always-on-top transparent overlay (PyQt5). The app can optionally export SRT captions with timestamps.

---

## Features

* Voice Activity Detection (webrtcvad) to avoid transcribing silence.
* Real-time segmentation of speech into short audio segments.
* Background worker queue with configurable concurrency for STT backends.
* Default STT backend: **VOSK** (modular backend interface — easy to plug Whisper or other services).
* Always‑on‑top translucent overlay window (PyQt5) with auto‑hide and styling for readable captions.
* Optional SRT export (timestamps written to a `.srt` file).
* Configurable parameters at the top of the file (sample rate, VAD aggressiveness, timeouts, number of workers, etc.).

---

## Requirements

* Python 3.8+ recommended

Python packages (example install):

```bash
pip install sounddevice numpy webrtcvad PyQt5 vosk
```

> Note: `vosk` is optional only if you plan to use the included VOSK backend. If you want to plug a different backend (e.g., OpenAI/Whisper), adapt `STTBackend` and the `build_stt_backend()` function accordingly.

You may also create a `requirements.txt` containing:

```
sounddevice
numpy
webrtcvad
PyQt5
vosk
```

---

## Quick start

1. Download or place a speech recognition model for VOSK and set the model path in `CONFIG['vosk_model_path']` (default: `model`).
2. Run the script:

```bash
python realtime_subtitle.py --model-path path/to/model --workers 1 --srt captions.srt
```

* `--model-path` — folder containing the VOSK model
* `--workers` — number of STT worker threads (increase if you have multiple CPU cores or a fast GPU-backed backend)
* `--srt` — output filename for SRT captions (optional)

If VOSK is not installed or `build_stt_backend()` cannot find an available backend, the program will exit with an error message; either install VOSK or implement/plug another backend.

---

## Configuration

At the top of the script there is a `CONFIG` dict with the following keys (defaults shown in the file):

* `sample_rate`: 16000 — sample rate for capture and STT.
* `block_duration`: 30 — ms per audio frame fed to VAD. (Allowed 10/20/30.)
* `channels`: 1 — number of input channels (mono recommended).
* `vad_aggressiveness`: 0–3 — VAD sensitivity. Higher = more aggressive at ignoring noise.
* `min_speech_ms`: 250 — minimum length (ms) for a valid speech segment.
* `max_silence_ms`: 700 — maximum silence (ms) within a segment before closing it.
* `segment_timeout_s`: 10 — force‑flush a long running segment.
* `stt_workers`: 1 — number of concurrent STT workers.
* `overlay_timeout_s`: 3.5 — auto-hide overlay after this many seconds without new captions.
* `srt_output`: `captions.srt` — default SRT output file.
* `vosk_model_path`: `model` — default VOSK model folder.

Adjust these parameters to suit your microphone, language, and latency needs.

---

## How it works (overview)

1. `RealTimeCapturer` opens a `sounddevice` input stream and pushes PCM16 frames into a queue.
2. `Segmenter` consumes frames and uses `webrtcvad` to group consecutive speech frames into `AudioSegment` objects, handling silence and timeouts.
3. `STTWorker` threads take completed segments, convert samples to bytes, and call the chosen `STTBackend.transcribe()` implementation.
4. Recognized text is displayed via the `CaptionOverlay` (PyQt5) and optionally written to an SRT file via `SRTWriter`.

The STT backend is modular — the included `VoskBackend` wraps the VOSK recognizer, but you can implement `STTBackend` for whisper/OpenAI/etc.

---

## SRT output details

The program writes SRT entries using `SRTWriter`. Timestamps are formatted as `HH:MM:SS,mmm`. Currently the timestamp implementation uses absolute epoch time converted to `hh:mm:ss,ms` (not relative to process start). You can adapt `_format_timestamp()` if you prefer offsets relative to the start of recording.

---

## Tips & Troubleshooting

* **No audio or crashes on start**: Ensure your microphone is accessible and `sounddevice` can open the default device. Run `python -m sounddevice` (or check sounddevice docs) to list available devices.
* **VOSK model not found**: Download a model from the VOSK project and set `CONFIG['vosk_model_path']` to the model's folder.
* **High CPU usage**: Lower `stt_workers`, reduce audio sample rate (if supported by your model), or use a more efficient backend.
* **False positives / background noise**: Increase `vad_aggressiveness` (0–3) or adjust `min_speech_ms` and `max_silence_ms`.
* **Overlay too big / small**: Modify font size in `CaptionOverlay` (font creation line) or tweak `overlay_timeout_s`.

---

## Extending / Plugging new STT backends

Create a new class implementing the `STTBackend` interface with a `transcribe(pcm_bytes: bytes, sample_rate: int) -> Tuple[str, float]` method. Then modify `build_stt_backend()` to return your backend (optionally via CLI flag).

Example backends to consider:

* Whisper (local or OpenAI Whisper API)
* Cloud STT APIs (Google, Azure, AWS Transcribe)

---

## Development & Testing

* Run with `--workers 1` while iterating to simplify debugging.
* Use logging (the script configures `logging.basicConfig`) to trace audio capture, VAD, and worker activity.
* Unit test `AudioSegment` and `SRTWriter` logic separately by feeding synthetic PCM data.

---

## License

MIT-style permissive license. Use, modify, and distribute freely. No warranty.
