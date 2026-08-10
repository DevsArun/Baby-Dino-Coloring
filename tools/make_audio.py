#!/usr/bin/env python3
"""Generate royalty-free background music + SFX for the app (numpy synth,
then ffmpeg -> ogg). 100% offline, 100% ours - zero copyright risk."""
import math
import os
import struct
import subprocess
import wave

import numpy as np

SR = 22050
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")


def save_wav(name, samples):
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767).astype(np.int16)
    path = os.path.join(OUT, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


def to_ogg(wav_path):
    ogg = wav_path.replace(".wav", ".ogg")
    enc = None
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"],
                           capture_output=True, text=True).stdout
    enc = "libvorbis" if "libvorbis" in probe else ("libmp3lame" if "libmp3lame" in probe else None)
    if enc == "libvorbis":
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                        "-c:a", "libvorbis", "-q:a", "3", ogg], check=True)
    elif enc == "libmp3lame":
        ogg = wav_path.replace(".wav", ".mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                        "-c:a", "libmp3lame", "-q:a", "4", ogg], check=True)
    else:  # last resort: keep wav
        return wav_path
    os.remove(wav_path)
    return ogg


def marimba(freq, start, dur, total, vol=0.5):
    """Marimba-like pluck: sine + soft 3rd harmonic, fast decay envelope."""
    n0 = int(start * SR)
    n1 = min(int((start + dur) * SR), len(total))
    t = np.arange(n1 - n0) / SR
    env = np.exp(-t * 9.0)
    wave_ = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(6 * np.pi * freq * t)
    total[n0:n1] += vol * env * wave_


def bass(freq, start, dur, total, vol=0.22):
    n0 = int(start * SR)
    n1 = min(int((start + dur) * SR), len(total))
    t = np.arange(n1 - n0) / SR
    env = np.minimum(1.0, t * 25.0) * np.exp(-t * 2.2)
    total[n0:n1] += vol * env * np.sin(2 * np.pi * freq * t)


def make_bg_loop():
    """Cheerful 16-bar loop, C-G-Am-F, 100 BPM."""
    bpm = 100.0
    beat = 60.0 / bpm
    bar = 4 * beat
    chords = [
        ("C", [261.63, 329.63, 392.00], 130.81),
        ("G", [246.94, 293.66, 392.00], 98.00),
        ("A", [261.63, 329.63, 440.00], 110.00),
        ("F", [261.63, 349.23, 440.00], 87.31),
    ]
    bars = 16
    total = np.zeros(int(bars * bar * SR) + SR)
    for b in range(bars):
        _, tones, root = chords[b % 4]
        t0 = b * bar
        # arpeggio eighth notes: up-down pattern
        pattern = [tones[0], tones[1], tones[2], tones[1] * 2,
                   tones[2], tones[1], tones[0], tones[1]]
        for i, fq in enumerate(pattern):
            marimba(fq, t0 + i * beat / 2, beat * 0.55, total,
                    vol=0.42 if i % 2 == 0 else 0.34)
        # bass on 1 and 3
        bass(root, t0, beat * 1.8, total)
        bass(root, t0 + 2 * beat, beat * 1.8, total)
    # gentle loop fade at both edges
    fade = int(0.15 * SR)
    total[:fade] *= np.linspace(0, 1, fade)
    total[-fade:] *= np.linspace(1, 0, fade)
    total *= 0.9 / max(1e-6, np.max(np.abs(total)))
    return total


def sweep(f0, f1, dur, vol=0.5, decay=9.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = np.linspace(f0, f1, n)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-t * decay) * np.minimum(1.0, t * 60.0)
    return vol * env * np.sin(phase)


def make_pop():
    return sweep(660, 1150, 0.10, vol=0.5, decay=22.0)


def make_fill():
    s = sweep(320, 860, 0.22, vol=0.4, decay=7.0)
    s += 0.15 * sweep(640, 1720, 0.22, decay=7.0)
    return s


def make_tada():
    dur = 1.1
    total = np.zeros(int(dur * SR) + SR)
    notes = [523.25, 659.25, 783.99, 1046.50]
    for i, fq in enumerate(notes):
        marimba(fq, i * 0.13, 0.6, total, vol=0.5)
    # final chord sparkle
    for fq in notes:
        marimba(fq, 0.55, 0.5, total, vol=0.25)
    total *= 0.9 / max(1e-6, np.max(np.abs(total)))
    return total


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for name, data in [
        ("bg_loop", make_bg_loop()),
        ("pop", make_pop()),
        ("fill", make_fill()),
        ("tada", make_tada()),
    ]:
        wav = save_wav(name + ".wav", data)
        final = to_ogg(wav)
        size_kb = os.path.getsize(final) / 1024
        made.append((os.path.basename(final), round(size_kb, 1)))
    print("AUDIO OK:", made)


if __name__ == "__main__":
    main()
