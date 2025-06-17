import gradio as gr
import subprocess, tempfile, os
import numpy as np
import soundfile as sf
import webrtcvad
from resemblyzer import VoiceEncoder, preprocess_wav, sampling_rate
import whisper
from sklearn.cluster import AgglomerativeClustering


def convert_to_wav(path):
    out = tempfile.mktemp(suffix=".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", path, "-ac", "1", "-ar", "16000", out
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return out


def speech_segments(wav):
    vad = webrtcvad.Vad(3)
    frame_ms = 30
    samples = int(sampling_rate * frame_ms / 1000)
    wav16 = (wav * 32768).astype(np.int16)
    flags = []
    for i in range(0, len(wav16) - samples, samples):
        frame = wav16[i:i+samples].tobytes()
        flags.append(vad.is_speech(frame, sampling_rate))
    segments = []
    start = None
    for idx, f in enumerate(flags):
        if f and start is None:
            start = idx
        elif not f and start is not None:
            segments.append((start*samples, idx*samples))
            start = None
    if start is not None:
        segments.append((start*samples, len(wav16)))
    return segments


def diarize(wav):
    segs = speech_segments(wav)
    if not segs:
        return [(0, len(wav)/sampling_rate, 0)]
    enc = VoiceEncoder("cpu")
    embeds = [enc.embed_utterance(wav[s:e]) for s, e in segs]
    n_clusters = min(2, len(embeds))
    labels = AgglomerativeClustering(n_clusters=n_clusters).fit_predict(embeds)
    return [(s/sampling_rate, e/sampling_rate, int(l)) for (s, e), l in zip(segs, labels)]


def assign_speaker(ts, diar):
    mid = (ts["start"] + ts["end"]) / 2
    for s, e, l in diar:
        if s <= mid <= e:
            return l
    return 0


def fmt(t):
    h = int(t//3600); t %= 3600
    m = int(t//60); s = t%60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.', ',')


def make_srt(res, diar):
    lines = []
    for i, seg in enumerate(res["segments"], 1):
        sp = assign_speaker(seg, diar)
        lines.append(f"{i}\n{fmt(seg['start'])} --> {fmt(seg['end'])}\n<S{sp+1}> {seg['text'].strip()}\n")
    return "\n".join(lines)


def process(file, language):
    wav_path = convert_to_wav(file)
    wav, _ = sf.read(wav_path)
    diar = diarize(wav)
    model = whisper.load_model("base")
    kwargs = {} if language == "Auto" else {"language": language}
    res = model.transcribe(wav_path, **kwargs)
    srt = make_srt(res, diar)
    out = tempfile.mktemp(suffix=".srt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(srt)
    return out


def main():
    langs = ["Auto", "en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh"]
    gr.Interface(
        fn=process,
        inputs=[gr.File(label="Audio/Video"), gr.Dropdown(langs, label="Language", value="Auto")],
        outputs=gr.File(label="Subtitle (.srt)"),
        title="Multilingual Transcriber",
        description="Upload an audio or video file to generate subtitles with speaker tags"
    ).launch()


if __name__ == "__main__":
    main()
