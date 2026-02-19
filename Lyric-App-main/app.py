"""
realtime_subtitle.py

Real-time subtitle/captioning app — scalable, modular, and useful.
Records microphone audio, uses VAD (webrtcvad) to detect speech segments,
sends segments to a worker pool for speech-to-text (default backend: VOSK),
and shows captions in a small always-on-top transparent overlay window.

Features:
- Voice Activity Detection to avoid transcribing silence.
- Background worker queue with configurable concurrency.
- Overlay captions (PyQt5) with auto-hide and styling.
- Optional SRT export with timestamps.
- Modular STT backend interface (VOSK provided). Easy to add Whisper/OpenAI backends.
- Configurable parameters at the top of the file.

Install (example):
    pip install sounddevice numpy webrtcvad PyQt5 vosk

Run:
    python realtime_subtitle.py
"""

from __future__ import annotations
import argparse
import queue
import threading
import time
import collections
import json
import os
import sys
import math
import wave
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

# Audio and VAD
import sounddevice as sd
import numpy as np
import webrtcvad

# GUI
from PyQt5 import QtCore, QtWidgets, QtGui

# STT backend: VOSK (default). Wrap import to allow optional backends.
try:
    from vosk import Model as VoskModel, KaldiRecognizer
    VOSK_AVAILABLE = True
except Exception:
    VOSK_AVAILABLE = False

# --------------- Configuration ---------------
CONFIG = {
    # Audio
    "sample_rate": 16000,         # VOSK/webrtcvad friendly
    "block_duration": 30,         # ms per audio frame fed to VAD (10/20/30 allowed)
    "channels": 1,

    # VAD aggressiveness (0-3). 3 is most aggressive (less false positives).
    "vad_aggressiveness": 2,

    # Speech segmentation
    "min_speech_ms": 250,         # minimum length to consider a speech segment (ms)
    "max_silence_ms": 700,        # max silence within speech before ending (ms)
    "segment_timeout_s": 10,      # force flush segment after N seconds

    # Worker pool for STT
    "stt_workers": 1,             # concurrency — increase if you have CPU/GPU

    # Overlay
    "overlay_timeout_s": 3.5,     # auto-hide after no new captions

    # Files
    "srt_output": "captions.srt",

    # Vosk model path (if installed locally)
    "vosk_model_path": "model",   # set to your VOSK model folder (e.g., "model")
}
# --------------- End config -------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class AudioSegment:
    """Represents a captured speech audio segment with timing info and PCM data."""
    start_time: float
    end_time: Optional[float] = None
    samples: List[np.ndarray] = field(default_factory=list)  # list of int16 numpy arrays

    def append(self, pcm_chunk: np.ndarray):
        self.samples.append(pcm_chunk)

    def get_pcm_bytes(self) -> bytes:
        """Return concatenated PCM16LE bytes suitable for VOSK."""
        if not self.samples:
            return b""
        concat = np.concatenate(self.samples)
        return concat.tobytes()

    def duration(self) -> float:
        if self.end_time is None:
            return 0.0
        return self.end_time - self.start_time


# ---------------- STT Backend Interface ----------------
class STTBackend:
    def transcribe(self, pcm_bytes: bytes, sample_rate: int) -> Tuple[str, float]:
        """
        Transcribe PCM16LE bytes.
        Returns: (text, confidence_estimate)
        """
        raise NotImplementedError


class VoskBackend(STTBackend):
    def __init__(self, model_path: str, sample_rate: int):
        if not VOSK_AVAILABLE:
            raise RuntimeError("VOSK not available (pip install vosk).")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"VOSK model not found at '{model_path}'. Download a model and set CONFIG['vosk_model_path']."
            )
        logging.info("Loading VOSK model (this may take a while)...")
        self.model = VoskModel(model_path)
        self.sample_rate = sample_rate

    def transcribe(self, pcm_bytes: bytes, sample_rate: int):
        rec = KaldiRecognizer(self.model, sample_rate)
        # Feed in chunks to avoid memory issues
        chunk_size = 4000
        pos = 0
        final_text = []
        while pos < len(pcm_bytes):
            piece = pcm_bytes[pos:pos + chunk_size]
            rec.AcceptWaveform(piece)
            pos += chunk_size
        res = rec.FinalResult()
        try:
            j = json.loads(res)
            text = j.get("text", "").strip()
            # VOSK doesn't always provide confidence; estimate by length
            conf = len(text) / max(1, len(pcm_bytes))  # crude proxy
            return text, conf
        except Exception:
            return "", 0.0


# ---------------- GUI Overlay ----------------
class CaptionOverlay(QtWidgets.QWidget):
    caption_signal = QtCore.pyqtSignal(str)

    def __init__(self, timeout: float = 3.0):
        super().__init__(flags=QtCore.Qt.WindowStaysOnTopHint)
        self.timeout = timeout
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Tool
            | QtCore.Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.label = QtWidgets.QLabel("", self)
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont("Sans Serif", 20)
        font.setBold(True)
        self.label.setFont(font)
        # Styling: semi-opaque rounded rectangle
        self.label.setStyleSheet(
            "QLabel { background-color: rgba(0,0,0,150); color: white; padding: 12px; border-radius: 10px; }"
        )
        self.hide_timer = QtCore.QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_caption)
        self.caption_signal.connect(self._set_caption)
        self._last_text = ""

    def show_caption(self, text: str):
        self.caption_signal.emit(text)

    @QtCore.pyqtSlot(str)
    def _set_caption(self, text: str):
        if not text.strip():
            return
        self._last_text = text.strip()
        self.label.setText(self._last_text)
        self.adjust_size_and_position()
        self.show()
        # Restart hide timer
        self.hide_timer.start(int(self.timeout * 1000))

    def hide_caption(self):
        self.hide()

    def adjust_size_and_position(self):
        screen = QtWidgets.QApplication.primaryScreen()
        rect = screen.geometry()
        maxw = int(rect.width() * 0.6)
        self.label.setMaximumWidth(maxw)
        self.label.adjustSize()
        # Place at bottom center above taskbar (approx)
        w = self.label.width()
        h = self.label.height()
        x = (rect.width() - w) // 2
        y = rect.height() - h - 120
        self.setGeometry(x, y, w, h)
        self.label.setGeometry(0, 0, w, h)


# ---------------- Audio Capture & VAD ----------------
class RealTimeCapturer:
    def __init__(self, sample_rate: int, block_duration_ms: int, vad_aggressiveness: int,
                 channels: int = 1):
        self.sample_rate = sample_rate
        self.block_duration_ms = block_duration_ms
        self.block_size = int(sample_rate * block_duration_ms / 1000)
        self.channels = channels
        self.vad = webrtcvad.Vad(max(0, min(3, vad_aggressiveness)))
        self.stream = None
        self.q = queue.Queue(maxsize=100)
        self.running = threading.Event()
        self.running.clear()

    def start(self):
        if self.running.is_set():
            return
        self.running.set()
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            blocksize=self.block_size,
            callback=self._callback,
        )
        self.stream.start()
        logging.info("Audio input stream started.")

    def stop(self):
        self.running.clear()
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        logging.info("Audio input stream stopped.")

    def _callback(self, indata, frames, time_info, status):
        """
        sounddevice callback: indata is int16 array shape (frames, channels)
        We push raw bytes to queue for VAD processing on a separate thread.
        """
        if status:
            logging.debug("Stream status: %s", status)
        # Mono: flatten
        if self.channels > 1:
            indata = indata.mean(axis=1).astype(np.int16)
        else:
            indata = indata.reshape(-1)
        # Put tuple (timestamp, pcm_bytes)
        ts = time.time()
        try:
            self.q.put_nowait((ts, indata.copy()))
        except queue.Full:
            logging.warning("Audio queue full; dropping audio frame.")


# ---------------- Segmenter (VAD -> Speech Segments) ----------------
class Segmenter(threading.Thread):
    def __init__(self, capturer: RealTimeCapturer, min_speech_ms: int, max_silence_ms: int,
                 segment_timeout_s: int, out_queue: queue.Queue):
        super().__init__(daemon=True)
        self.capturer = capturer
        self.min_frames = max(1, int(math.ceil(min_speech_ms / capturer.block_duration_ms)))
        self.max_silence_frames = max(1, int(math.ceil(max_silence_ms / capturer.block_duration_ms)))
        self.segment_timeout_s = segment_timeout_s
        self.out_queue = out_queue
        self._stop = threading.Event()
        self._stop.clear()

    def run(self):
        cur_segment: Optional[AudioSegment] = None
        speech_frame_count = 0
        silence_frame_count = 0
        last_activity = None

        logging.info("Segmenter thread started.")
        while not self._stop.is_set():
            try:
                ts, pcm = self.capturer.q.get(timeout=0.1)
            except queue.Empty:
                continue

            is_speech = self.capturer.vad.is_speech(pcm.tobytes(), self.capturer.sample_rate)
            # Start new segment
            if cur_segment is None:
                if is_speech:
                    cur_segment = AudioSegment(start_time=ts)
                    cur_segment.append(pcm)
                    speech_frame_count = 1
                    silence_frame_count = 0
                    last_activity = ts
                # else ignore leading silence
            else:
                # Append always while in segment (helps continuity)
                cur_segment.append(pcm)
                if is_speech:
                    speech_frame_count += 1
                    silence_frame_count = 0
                    last_activity = ts
                else:
                    silence_frame_count += 1

                # If enough silence frames -> end segment
                if silence_frame_count >= self.max_silence_frames:
                    cur_segment.end_time = last_activity or ts
                    duration_ms = (cur_segment.end_time - cur_segment.start_time) * 1000
                    if duration_ms >= self.min_frames * self.capturer.block_duration_ms:
                        # emit segment
                        try:
                            self.out_queue.put_nowait(cur_segment)
                        except queue.Full:
                            logging.warning("Out queue full; dropping segment.")
                    # reset
                    cur_segment = None
                    speech_frame_count = 0
                    silence_frame_count = 0
                    last_activity = None
                else:
                    # Force flush if too long
                    if (ts - cur_segment.start_time) > self.segment_timeout_s:
                        cur_segment.end_time = ts
                        try:
                            self.out_queue.put_nowait(cur_segment)
                        except queue.Full:
                            logging.warning("Out queue full; dropping long segment.")
                        cur_segment = None
                        speech_frame_count = 0
                        silence_frame_count = 0
                        last_activity = None

        logging.info("Segmenter thread stopping.")

    def stop(self):
        self._stop.set()


# ---------------- Worker Pool ----------------
class STTWorker(threading.Thread):
    def __init__(self, stt_backend: STTBackend, in_queue: queue.Queue, ui_callback, srt_writer):
        super().__init__(daemon=True)
        self.stt = stt_backend
        self.in_queue = in_queue
        self.ui_callback = ui_callback  # function to call to display captions
        self.srt_writer = srt_writer
        self._stop = threading.Event()
        self._stop.clear()
        self.seq = 1

    def run(self):
        logging.info("STT worker started.")
        while not self._stop.is_set():
            try:
                seg: AudioSegment = self.in_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            # Transcribe
            pcm_bytes = seg.get_pcm_bytes()
            try:
                text, conf = self.stt.transcribe(pcm_bytes, CONFIG["sample_rate"])
            except Exception as e:
                logging.exception("STT backend error: %s", e)
                text, conf = "", 0.0
            if text:
                # Send to UI
                self.ui_callback(text)
                # Write SRT entry
                self.srt_writer.write_entry(self.seq, seg.start_time, seg.end_time or seg.start_time, text)
                self.seq += 1
            # else ignore empty results
        logging.info("STT worker stopping.")

    def stop(self):
        self._stop.set()


# ---------------- SRT Writer ----------------
class SRTWriter:
    def __init__(self, filename: str):
        self.filename = filename
        # create/clear
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("")

    @staticmethod
    def _format_timestamp(ts: float) -> str:
        # ts is epoch seconds; need to convert to hours:mins:secs,millis
        # For SRT we present relative times (start from 0). To keep it simple, we will use absolute times relative to process start.
        total_ms = int(ts * 1000)
        ms = total_ms % 1000
        s = (total_ms // 1000) % 60
        m = (total_ms // (1000 * 60)) % 60
        h = (total_ms // (1000 * 60 * 60)) % 100
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    def write_entry(self, idx: int, start_ts: float, end_ts: float, text: str):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"{idx}\n")
            f.write(f"{self._format_timestamp(start_ts)} --> {self._format_timestamp(end_ts)}\n")
            f.write(text + "\n\n")


# ---------------- Main Application ----------------
def build_stt_backend() -> STTBackend:
    # Default: VOSK backend if available
    if VOSK_AVAILABLE:
        return VoskBackend(CONFIG["vosk_model_path"], CONFIG["sample_rate"])
    else:
        raise RuntimeError("No STT backend available. Please install VOSK and set model path in CONFIG.")


def main_app():
    # CLI options
    parser = argparse.ArgumentParser(description="Real-time subtitle/captioning overlay.")
    parser.add_argument("--sample-rate", type=int, default=CONFIG["sample_rate"])
    parser.add_argument("--model-path", type=str, default=CONFIG["vosk_model_path"])
    parser.add_argument("--workers", type=int, default=CONFIG["stt_workers"])
    parser.add_argument("--srt", type=str, default=CONFIG["srt_output"])
    args = parser.parse_args()

    # Update config
    CONFIG["sample_rate"] = args.sample_rate
    CONFIG["vosk_model_path"] = args.model_path
    CONFIG["stt_workers"] = max(1, args.workers)
    CONFIG["srt_output"] = args.srt

    # Build STT backend
    try:
        stt_backend = build_stt_backend()
    except Exception as e:
        logging.error("Failed to initialize STT backend: %s", e)
        sys.exit(1)

    # Queues
    segments_queue = queue.Queue(maxsize=50)

    # Audio capture
    capturer = RealTimeCapturer(
        sample_rate=CONFIG["sample_rate"],
        block_duration_ms=CONFIG["block_duration"],
        vad_aggressiveness=CONFIG["vad_aggressiveness"],
        channels=CONFIG["channels"],
    )

    # Segmenter
    segmenter = Segmenter(
        capturer=capturer,
        min_speech_ms=CONFIG["min_speech_ms"],
        max_silence_ms=CONFIG["max_silence_ms"],
        segment_timeout_s=CONFIG["segment_timeout_s"],
        out_queue=segments_queue,
    )

    # SRT writer
    srt_writer = SRTWriter(CONFIG["srt_output"])

    # Set up Qt app and overlay
    app = QtWidgets.QApplication(sys.argv)
    overlay = CaptionOverlay(timeout=CONFIG["overlay_timeout_s"])

    # UI callback for workers to show captions
    def ui_cb(text: str):
        # Forward to Qt thread
        overlay.show_caption(text)

    # Worker pool
    workers = []
    for _ in range(CONFIG["stt_workers"]):
        w = STTWorker(stt_backend=stt_backend, in_queue=segments_queue, ui_callback=ui_cb, srt_writer=srt_writer)
        workers.append(w)

    # Start everything
    try:
        capturer.start()
        segmenter.start()
        for w in workers:
            w.start()
        # Show a small help overlay at start
        overlay.show_caption("Captions running — press Ctrl+C to stop")
        logging.info("Application running. Press Ctrl+C to exit.")
        # Qt event loop (blocking)
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received — shutting down.")
    finally:
        # Clean stop
        segmenter.stop()
        capturer.stop()
        for w in workers:
            w.stop()
        time.sleep(0.2)


if __name__ == "__main__":
    main_app()
