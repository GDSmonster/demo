# -*- coding: utf-8 -*-
"""
明天会更好 · 歌词自动切分（强制对齐）

用法:
    python split_lyrics.py --audio 明天会更好.mp3 --lyrics lyrics.txt --out output.json

依赖:
    pip install faster-whisper

说明:
    1. 先用 faster-whisper 做带词级时间戳的识别
    2. 把识别出的词序列与你提供的歌词逐行做序列对齐(difflib)
    3. 每行歌词取其首词 start 与末词 end 作为起止时间
    4. 输出 JSON(含每行 start/end/text) 与 LRC 文件
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

import numpy as np


def clean_text(s: str) -> str:
    """去掉标点和空白，仅保留可对齐的字符，用于序列匹配。"""
    return re.sub(r"[\s，。、！？；：,.!?;:…—\-\"'“”‘’（）()\[\]【】《》]", "", s)


def load_lyrics(path: Path) -> list[str]:
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        t = raw.strip()
        if t:
            lines.append(t)
    return lines


def transcribe(audio_path: str):
    """返回 (words: list[(word, start, end)], full_text: str)"""
    from faster_whisper import WhisperModel

    # large-v3 中文识别最稳；机器一般可跑 medium 或 small
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        audio_path,
        language="zh",
        word_timestamps=True,
        vad_filter=True,
        initial_prompt="明天会更好，轻轻敲醒沉睡的心灵。",
    )

    words = []
    full = []
    for seg in segments:
        for w in seg.words or []:
            wt = (w.word or "").strip()
            if not wt:
                continue
            words.append((wt, float(w.start), float(w.end)))
            full.append(wt)
    return words, "".join(full)


def align_lines(words, lyrics_lines):
    """
    把歌词的每一行映射到 words 子序列，返回 [(text, start, end)]。
    策略：把所有 word 拼成一个干净串，把歌词也拼成一个干净串，
    用 difflib.SequenceMatcher 找匹配块，再按行长度切回每行。
    """
    word_chars = [clean_text(w) for w, _, _ in words]
    word_starts = [s for _, s, _ in words]
    word_ends = [e for _, _, e in words]

    # 逐字序列：每个 word 可能含多字，拆成单字并记录所属 word index
    char_to_word = []
    char_seq = []
    for wi, wc in enumerate(word_chars):
        for ch in wc:
            char_seq.append(ch)
            char_to_word.append(wi)

    # 歌词也拆成单字序列，并记录每个字属于哪一行
    line_chars = []
    char_to_line = []
    for li, line in enumerate(lyrics_lines):
        for ch in clean_text(line):
            line_chars.append(ch)
            char_to_line.append(li)

    # SequenceMatcher 对齐两个单字序列
    sm = difflib.SequenceMatcher(a=char_seq, b=line_chars, autojunk=False)
    # 记录每个歌词字对应的 word index
    line_word_idx = [[] for _ in lyrics_lines]  # 每行匹配到的 word index 列表

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(j2 - j1):
                ch_off = j1 + k
                wo_off = i1 + k
                if wo_off < len(char_to_word) and ch_off < len(char_to_line):
                    line_word_idx[char_to_line[ch_off]].append(char_to_word[wo_off])

    result = []
    for li, line in enumerate(lyrics_lines):
        idxs = line_word_idx[li]
        if idxs:
            # 去重并保持顺序
            seen = set()
            uniq = []
            for x in idxs:
                if x not in seen:
                    seen.add(x)
                    uniq.append(x)
            start = word_starts[uniq[0]]
            end = word_ends[uniq[-1]]
        else:
            # 没匹配到，用上一行的 end 兜底
            start = result[-1]["end"] if result else 0.0
            end = start + 2.0
        result.append({"text": line, "start": round(start, 2), "end": round(end, 2)})
    return result


def to_lrc(lines):
    out = []
    for l in lines:
        m = int(l["start"]) // 60
        s = l["start"] - m * 60
        out.append(f"[{m:02d}:{s:05.2f}]{l['text']}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True, help="解密后的 mp3/flac/wav 路径")
    ap.add_argument("--lyrics", required=True, help="纯文本歌词，每行一句")
    ap.add_argument("--out", default="lyrics_timed.json")
    args = ap.parse_args()

    audio = Path(args.audio)
    if not audio.exists():
        sys.exit(f"音频文件不存在: {audio}")

    lyrics_lines = load_lyrics(Path(args.lyrics))
    print(f"[1/3] 加载歌词 {len(lyrics_lines)} 行")

    print("[2/3] Whisper 识别中（首次会下载模型，约 3GB）...")
    words, full = transcribe(str(audio))
    print(f"      识别到 {len(words)} 个词，文本长度 {len(full)}")

    print("[3/3] 与提供的歌词做强制对齐...")
    timed = align_lines(words, lyrics_lines)

    out_json = Path(args.out)
    out_json.write_text(json.dumps(timed, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(out_json.with_suffix(".lrc")).write_text(to_lrc(timed), encoding="utf-8")

    print(f"\n完成！输出：")
    print(f"  JSON: {out_json}")
    print(f"  LRC : {out_json.with_suffix('.lrc')}")
    print("\n前 5 行预览：")
    for l in timed[:5]:
        print(f"  [{l['start']:6.2f} - {l['end']:6.2f}] {l['text']}")


if __name__ == "__main__":
    main()
