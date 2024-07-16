import tkinter as tk
from tkinter import simpledialog
import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from PIL import Image, ImageEnhance
import os
from datetime import datetime

def record_audio():
    # テキスト入力からファイル名の最初の部分を取得
    user_input = file_name_entry.get()
    if not user_input:
        print("ファイル名を入力してください")
        return
    user_input = user_input[:7]  # 最初の7文字を取得

    # 現在の日時を使用して一意のファイル名を生成
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_filename = user_input + "_" + timestamp
    WAVE_OUTPUT_FILENAME = f"{base_filename}.wav"
    SPECTROGRAM_OUTPUT_FILENAME = f"{base_filename}_spectrogram.png"
    CONTRASTED_OUTPUT_FILENAME = f"{base_filename}_contrasted.png"

    # 録音の設定
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 1

    audio = pyaudio.PyAudio()

    # 録音開始
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("録音中...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("録音終了")

    # 録音を停止
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 録音データをWAVファイルとして保存
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    # 録音した音声データをロード
    audio_path = WAVE_OUTPUT_FILENAME
    audio = AudioSegment.from_wav(audio_path)

    # 音声データをnumpy配列に変換
    raw_data = np.frombuffer(audio.raw_data, dtype=np.int16)

    # スペクトログラムを生成
    fig, ax = plt.subplots(figsize=(2.24, 2.24), dpi=100)  # 224x224ピクセルに対応するサイズと解像度
    ax.specgram(raw_data, NFFT=1024, Fs=RATE, noverlap=512)
    ax.axis('off')  # 軸を非表示にする

    # 生成されたスペクトログラムを保存
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(SPECTROGRAM_OUTPUT_FILENAME, bbox_inches='tight', pad_inches=0, dpi=100)
    plt.close()

    # コントラストを強調
    image = Image.open(SPECTROGRAM_OUTPUT_FILENAME)
    enhancer = ImageEnhance.Contrast(image)
    contrasted_image = enhancer.enhance(2.0)  # コントラストを強調する係数
    contrasted_image.save(CONTRASTED_OUTPUT_FILENAME)

    print(f"録音ファイル: {WAVE_OUTPUT_FILENAME}")
    print(f"スペクトログラム画像: {SPECTROGRAM_OUTPUT_FILENAME}")
    print(f"コントラスト強調画像: {CONTRASTED_OUTPUT_FILENAME}")

    # 保存されたファイルのリストを表示
    updated_files = os.listdir('.')
    print(updated_files)

# GUIの設定
root = tk.Tk()
root.title("Audio Recorder")

# ファイル名入力エリア
file_name_label = tk.Label(root, text="Enter file name (max 7 characters):")
file_name_label.pack(pady=5)
file_name_entry = tk.Entry(root, width=20)
file_name_entry.pack(pady=5)

# 録音ボタン
record_button = tk.Button(root, text="Record Audio", command=record_audio)
record_button.pack(pady=20)

root.mainloop()

