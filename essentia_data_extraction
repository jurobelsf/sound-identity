!pip install essentia

from google.colab import drive
import essentia.standard as es
import pandas as pd
import numpy as np
import os

drive.mount('/content/drive')

carpeta = '/content/drive/MyDrive/Canciones proyecto voam/control_songs_normalized/'
salida = '/content/drive/MyDrive/Canciones proyecto voam/matriz_control.xlsx'

extractor = es.MusicExtractor()

variables = (
    "lowlevel.spectral_centroid",
    "lowlevel.barkbands_flatness_db",
    "lowlevel.dissonance",
    "lowlevel.spectral_complexity",
    "lowlevel.spectral_flux",
    "lowlevel.spectral_energy",
    "lowlevel.silence_rate_30dB",
    "lowlevel.barkbands",
    "lowlevel.mfcc",
    "lowlevel.spectral_contrast_coeffs"
)

estadisticas = (
    ".mean", ".var", ".dmean", ".dvar", ".dmean2", ".dvar2"
)

datos = []

archivos = [
    f for f in os.listdir(carpeta)
    if f.lower().endswith(('.mp3', '.wav', '.flac'))
]

print("Archivos encontrados:", len(archivos))

for n, archivo in enumerate(archivos, 1):

    ruta = os.path.join(carpeta, archivo)
    print(n, "/", len(archivos), archivo)

    try:
        stats, frames = extractor(ruta)

        cancion = {"Nombre_Archivo": archivo}

        for key in stats.descriptorNames():

            if not key.endswith(estadisticas):
                continue

            sirve = False

            for variable in variables:
                if key.startswith(variable + "."):
                    sirve = True
                    break

            if not sirve:
                continue

            valor = stats[key]

            if isinstance(valor, (int, float, np.float32, np.float64)):
                cancion[key] = valor

            elif isinstance(valor, (list, np.ndarray)):
                valor = np.array(valor)

                if valor.ndim == 1:
                    for i, v in enumerate(valor):
                        cancion[key + "_" + str(i)] = v

        datos.append(cancion)

    except Exception as e:
        print("Error:", archivo, e)

df = pd.DataFrame(datos)

print()
print("Filas:", df.shape[0])
print("Variables:", df.shape[1])

df.to_excel(salida, index=False)

print("Archivo guardado en:", salida)
