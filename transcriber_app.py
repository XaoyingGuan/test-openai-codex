import gradio as gr
import subprocess
import tempfile
import os
import numpy as np
import soundfile as sf
import webrtcvad
from resemblyzer import VoiceEncoder, sampling_rate
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
        lines.append(
            f"{i}\n{fmt(seg['start'])} --> {fmt(seg['end'])}\n<S{sp+1}> {seg['text'].strip()}\n"
        )
    return "\n".join(lines)


def fmt_ass(t):
    h = int(t // 3600)
    t %= 3600
    m = int(t // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def make_ass(res, diar):
    header = (
        "[Script Info]\nScriptType: v4.00+\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,"
        "BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,"
        "BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
        "Style: Default,Arial,40,&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,-1,0,"
        "0,0,100,100,0,0,1,2,0,2,10,10,10,1\n\n"
        "[Events]\n"
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text"
    )
    lines = [header]
    for seg in res["segments"]:
        sp = assign_speaker(seg, diar)
        lines.append(
            f"Dialogue: 0,{fmt_ass(seg['start'])},{fmt_ass(seg['end'])},Default,S{sp+1},0,0,0,,{seg['text'].strip()}"
        )
    return "\n".join(lines)


def process(file, language, output):
    wav_path = convert_to_wav(file)
    wav, _ = sf.read(wav_path)
    diar = diarize(wav)
    model = whisper.load_model("base")
    kwargs = {} if language == "Auto" else {"language": language}
    res = model.transcribe(wav_path, **kwargs)

    if output == "srt":
        text = make_srt(res, diar)
        suffix = ".srt"
    else:
        text = make_ass(res, diar)
        suffix = ".ass"

    out = tempfile.mktemp(suffix=suffix)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)

    os.remove(wav_path)
    return out


def main():
    langs = ["Auto", "en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh"]
    formats = ["srt", "ass"]
    gr.Interface(
        fn=process,
        inputs=[
            gr.File(label="Audio/Video"),
            gr.Dropdown(langs, label="Language", value="Auto"),
            gr.Dropdown(formats, label="Format", value="srt"),
        ],
        outputs=gr.File(label="Subtitle"),
        title="Multilingual Transcriber",
        description="Upload an audio or video file to generate subtitles with speaker tags"
    ).launch()


if __name__ == "__main__":
    main()
