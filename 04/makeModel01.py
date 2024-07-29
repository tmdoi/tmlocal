import tkinter as tk
import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from PIL import Image, ImageEnhance
import os
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras.preprocessing.image import ImageDataGenerator

record_count = 0
dataset_dir = "dataset"

def record_audio():
    global record_count
    record_count += 1

    # テキスト入力からファイル名の最初の部分を取得
    user_input = file_name_entry.get()
    if not user_input:
        print("ファイル名を入力してください")
        return
    user_input = user_input[:7]  # 最初の7文字を取得

    # フォルダを作成または確認
    if not os.path.exists(user_input):
        os.makedirs(user_input)

    # 現在の日時を使用して一意のファイル名を生成
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_filename = user_input + "_" + timestamp
    WAVE_OUTPUT_FILENAME = os.path.join(user_input, f"{base_filename}.wav")
    SPECTROGRAM_OUTPUT_FILENAME = os.path.join(user_input, f"{base_filename}_spectrogram.png")
    CONTRASTED_OUTPUT_FILENAME = os.path.join(user_input, f"{base_filename}_contrasted.png")

    # 録音の設定
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 1

    audio = pyaudio.PyAudio()

    # インジケータを赤に変更して録音回数を表示
    indicator_label.config(bg='red', text=f"Recording... {record_count}")
    root.update()

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

    # インジケータを元に戻す
    indicator_label.config(bg='grey', text=f"Idle ({record_count})")
    root.update()

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

    # 保存されたファイルをデータセットディレクトリにコピー
    dataset_class_dir = os.path.join(dataset_dir, user_input)
    if not os.path.exists(dataset_class_dir):
        os.makedirs(dataset_class_dir)
    contrasted_image.save(os.path.join(dataset_class_dir, f"{base_filename}_contrasted.png"))

    # 保存されたファイルのリストを表示
    updated_files = os.listdir(user_input)
    print(updated_files)

def quit_program():
    root.destroy()

def train_model():
    # データジェネレータの設定
    datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

    train_generator = datagen.flow_from_directory(
        dataset_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )

    validation_generator = datagen.flow_from_directory(
        dataset_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )

    # モデルの構築
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(train_generator.num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # モデルのトレーニング
    model.fit(
        train_generator,
        epochs=10,
        validation_data=validation_generator
    )

    # モデルの保存
    model.save('audio_classification_model.h5')
    print("モデルが保存されました")

# GUIの設定
root = tk.Tk()
root.title("Audio Recorder")

# ファイル名入力エリア
file_name_label = tk.Label(root, text="Enter file name (max 7 characters):")
file_name_label.pack(pady=5)
file_name_entry = tk.Entry(root, width=20)
file_name_entry.pack(pady=5)

# インジケータラベル
indicator_label = tk.Label(root, text="Idle (0)", bg='grey', width=20, height=2)
indicator_label.pack(pady=5)

# 録音ボタン
record_button = tk.Button(root, text="Record Audio", command=record_audio)
record_button.pack(pady=10)

# トレーニングボタン
train_button = tk.Button(root, text="Train Model", command=train_model)
train_button.pack(pady=10)

# 終了ボタン
quit_button = tk.Button(root, text="Quit", command=quit_program)
quit_button.pack(pady=10)

root.mainloop()

