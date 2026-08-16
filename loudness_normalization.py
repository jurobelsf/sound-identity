!pip install pyloudnorm pydub soundfile

import os
import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from pydub import AudioSegment
from google.colab import drive

drive.mount('/content/drive', force_remount=True)

carpeta_origen = '/content/drive/MyDrive/Canciones proyecto voam/control songs/'
carpeta_destino = '/content/drive/MyDrive/Canciones proyecto voam/control_songs_normalized/'

if os.path.exists(carpeta_destino):
    for f in os.listdir(carpeta_destino):
        if f.lower().endswith('.wav'):
            os.remove(os.path.join(carpeta_destino, f))
else:
    os.makedirs(carpeta_destino)

TARGET_LUFS = -14.0
TOLERANCIA_LUFS = 0.5

archivos = [
    f for f in os.listdir(carpeta_origen)
    if f.lower().endswith(('.mp3', '.wav', '.flac'))
]

print("Archivos encontrados:", len(archivos))

aceptados = 0
descartados = 0

for i, archivo in enumerate(archivos, 1):

    ruta_in = os.path.join(carpeta_origen, archivo)

    nombre = os.path.splitext(archivo)[0]
    ruta_out = os.path.join(
        carpeta_destino,
        nombre + '_norm.wav'
    )

    try:
        audio = AudioSegment.from_file(ruta_in)

        sr = audio.frame_rate
        canales = audio.channels

        samples = np.array(
            audio.get_array_of_samples(),
            dtype=np.float32
        )

        max_val = float(1 << (8 * audio.sample_width - 1))
        samples = samples / max_val

        if canales > 1:
            samples = samples.reshape((-1, canales))

        meter = pyln.Meter(sr)

        lufs = meter.integrated_loudness(samples)

        audio_norm = pyln.normalize.loudness(
            samples,
            lufs,
            TARGET_LUFS
        )

        peak = np.max(np.abs(audio_norm))

        if peak >= 1.0:
            audio_norm = (audio_norm / peak) * 0.99

        lufs_final = meter.integrated_loudness(audio_norm)

        if abs(lufs_final - TARGET_LUFS) <= TOLERANCIA_LUFS:

            sf.write(
                ruta_out,
                audio_norm,
                sr,
                subtype='PCM_24'
            )

            aceptados += 1

            print(
                f"[{i}/{len(archivos)}] Aceptado: "
                f"{archivo[:30]} | {lufs_final:.2f} LUFS"
            )

        else:

            descartados += 1

            print(
                f"[{i}/{len(archivos)}] Descartado: "
                f"{archivo[:30]} | {lufs_final:.2f} LUFS"
            )

    except Exception as e:

        descartados += 1
        print(
            f"[{i}/{len(archivos)}] Error: "
            f"{archivo} | {e}"
        )

print("\n" + "=" * 50)
print("RESULTADO")
print("=" * 50)
print("Procesadas:", len(archivos))
print("Aceptadas:", aceptados)
print("Descartadas:", descartados)
print("=" * 50)
