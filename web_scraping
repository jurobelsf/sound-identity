import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_DEST = os.path.join(BASE_DIR, "control songs")
PAUSA_SEG = 0.5

os.makedirs(CARPETA_DEST, exist_ok=True)

entrada = input("Ingresa el número de la página que quieres procesar (ej: 2): ")
NUM_PAGINA = entrada.strip()

nombre_pagina = f"pagina{NUM_PAGINA}.html"
ruta_pagina = os.path.join(BASE_DIR, nombre_pagina)

if not os.path.exists(ruta_pagina):
    print(f"No se encontró el archivo '{nombre_pagina}'.")
    exit()


def sanitizar(nombre):
    nombre = re.sub(r'[<>:"/\\|?*\n\r\t]', '', nombre)
    nombre = nombre.strip(". ")
    return nombre or "sin_nombre"


artistas_vistos = set()

for archivo in os.listdir(CARPETA_DEST):
    if archivo.endswith(".mp3"):
        nombre = archivo[:-4]
        partes = nombre.split(" - ")

        if len(partes) >= 2:
            artista = partes[-1]
            artistas_vistos.add(artista)

print(f"Artistas que ya están en la carpeta: {len(artistas_vistos)}")


def extraer_tracks(nodo, apollo_state, track_actual=None, lista=None, urls_vistas=None):

    if lista is None:
        lista = []

    if urls_vistas is None:
        urls_vistas = set()

    if isinstance(nodo, dict):

        if "artists" in nodo and ("name" in nodo or "title" in nodo):
            track_actual = nodo

        for value in nodo.values():

            if isinstance(value, str) and ".LOFI.mp3" in value:

                if value in urls_vistas:
                    continue

                urls_vistas.add(value)

                artista = "Desconocido"
                titulo = "Sin título"

                if track_actual:
                    titulo = track_actual.get("name") or track_actual.get("title") or "Sin título"

                    lista_artistas = track_actual.get("artists", [])

                    if isinstance(lista_artistas, list) and len(lista_artistas) > 0:
                        primero = lista_artistas[0]

                        if isinstance(primero, dict):

                            if "__ref" in primero:
                                ref = primero["__ref"]
                                artista = apollo_state.get(ref, {}).get(
                                    "name", "Desconocido"
                                )
                            else:
                                artista = primero.get("name", "Desconocido")

                        elif isinstance(primero, str):
                            artista = primero

                lista.append({
                    "titulo": titulo,
                    "artista": artista,
                    "url": value
                })

        for value in nodo.values():
            extraer_tracks(
                value,
                apollo_state,
                track_actual,
                lista,
                urls_vistas
            )

    elif isinstance(nodo, list):

        for item in nodo:
            extraer_tracks(
                item,
                apollo_state,
                track_actual,
                lista,
                urls_vistas
            )

    return lista


print(f"Procesando {nombre_pagina}...")

with open(ruta_pagina, "r", encoding="utf-8") as f:
    contenido = f.read()

soup_crudo = BeautifulSoup(contenido, "html.parser")

lineas_codigo = soup_crudo.find_all("td", class_="line-content")

if lineas_codigo:
    html_real = "\n".join(linea.get_text() for linea in lineas_codigo)
    soup = BeautifulSoup(html_real, "html.parser")
else:
    soup = soup_crudo

script_nodo = soup.find("script", id="__NEXT_DATA__")

if not script_nodo:
    print("__NEXT_DATA__ no encontrado.")
    exit()

datos_json = json.loads(script_nodo.string)

apollo = datos_json.get(
    "props", {}
).get(
    "pageProps", {}
).get(
    "apolloState", {}
)

todos_los_tracks = extraer_tracks(datos_json, apollo)


tracks_finales = []

for track in todos_los_tracks:

    artista = sanitizar(track["artista"])

    if artista != "Desconocido" and artista not in artistas_vistos:
        artistas_vistos.add(artista)
        tracks_finales.append(track)


print(f"Tracks encontrados: {len(todos_los_tracks)}")
print(f"Tracks nuevos: {len(tracks_finales)}")

if len(tracks_finales) == 0:
    print("No hay audios nuevos para descargar.")
    exit()


print(f"Descargando en: {CARPETA_DEST}")

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
})

exitosas = 0
fallidas = 0

for idx, track in enumerate(tracks_finales, 1):

    titulo = sanitizar(track["titulo"])
    artista = sanitizar(track["artista"])

    nombre_archivo = f"{titulo} - {artista}.mp3"
    ruta_destino = os.path.join(CARPETA_DEST, nombre_archivo)

    print(f"[{idx}/{len(tracks_finales)}] {nombre_archivo}")

    try:

        respuesta = session.get(track["url"], timeout=20)
        respuesta.raise_for_status()

        with open(ruta_destino, "wb") as f:
            f.write(respuesta.content)

        kb = len(respuesta.content) / 1024

        print(f"Guardado ({kb:.1f} KB)")
        exitosas += 1

    except requests.exceptions.RequestException as e:

        print(f"Error: {e}")
        fallidas += 1

    time.sleep(PAUSA_SEG)


print("\n" + "=" * 40)
print(f"Descargas exitosas: {exitosas}")
print(f"Descargas fallidas: {fallidas}")
print(f"Carpeta: {CARPETA_DEST}")
