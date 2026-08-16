import pandas as pd
import numpy as np

SEED = 42
UMBRAL_CORRELACION = 0.60

rng = np.random.default_rng(SEED)

df_voam = pd.read_excel(
    '/content/drive/MyDrive/Canciones proyecto voam/matriz_voam.xlsx'
)

df_control = pd.read_excel(
    '/content/drive/MyDrive/Canciones proyecto voam/matriz_control.xlsx'
)

df_voam['Etiqueta'] = 1
df_control['Etiqueta'] = 0

df_total = pd.concat(
    [df_voam, df_control],
    ignore_index=True
)

ruta_completa = (
    '/content/drive/MyDrive/Canciones proyecto voam/'
    'dataset_completo_sin_filtro.xlsx'
)

df_total.to_excel(ruta_completa, index=False)

nombres_archivos = df_total['Nombre_Archivo']
y = df_total['Etiqueta']

X = df_total.drop(
    columns=['Nombre_Archivo', 'Etiqueta']
)

print("\nCanciones:", X.shape[0])
print("Variables:", X.shape[1])

variables_constantes = X.columns[
    X.nunique(dropna=True) <= 1
].tolist()

if variables_constantes:
    X = X.drop(columns=variables_constantes)
    print("Variables constantes eliminadas:", len(variables_constantes))

print("\nCalculando correlaciones...")

matriz_corr = X.corr(
    method='spearman'
).abs()

variables = list(X.columns)
rng.shuffle(variables)

variables_conservadas = []
variables_eliminadas = []

for variable in variables:

    conservar = True

    for variable_guardada in variables_conservadas:

        correlacion = matriz_corr.loc[
            variable,
            variable_guardada
        ]

        if pd.notna(correlacion) and correlacion > UMBRAL_CORRELACION:

            conservar = False

            variables_eliminadas.append({
                'Variable_eliminada': variable,
                'Variable_conservada': variable_guardada,
                'Correlacion_abs': correlacion
            })

            break

    if conservar:
        variables_conservadas.append(variable)

X_limpio = X[variables_conservadas].copy()

print("\n" + "=" * 50)
print("RESULTADO")
print("=" * 50)
print("Variables originales:", X.shape[1])
print("Variables conservadas:", len(variables_conservadas))
print("Variables eliminadas:", len(variables_eliminadas))
print("Umbral:", UMBRAL_CORRELACION)

df_eliminadas = pd.DataFrame(
    variables_eliminadas
)

if len(df_eliminadas) > 0:

    df_eliminadas = df_eliminadas.sort_values(
        'Correlacion_abs',
        ascending=False
    )

    print("\nAlgunos pares eliminados:")
    print(
        df_eliminadas.head(20).to_string(index=False)
    )

df_final_modelo = pd.concat(
    [
        nombres_archivos,
        X_limpio,
        y
    ],
    axis=1
)

ruta_salida = (
    '/content/drive/MyDrive/Canciones proyecto voam/'
    'dataset_final_para_modelo_v3.xlsx'
)

df_final_modelo.to_excel(
    ruta_salida,
    index=False
)

ruta_registro = (
    '/content/drive/MyDrive/Canciones proyecto voam/'
    'registro_filtro_spearman_v3.xlsx'
)

with pd.ExcelWriter(ruta_registro) as writer:

    pd.DataFrame({
        'Variable_conservada': variables_conservadas
    }).to_excel(
        writer,
        sheet_name='Variables_conservadas',
        index=False
    )

    if len(df_eliminadas) > 0:
        df_eliminadas.to_excel(
            writer,
            sheet_name='Variables_eliminadas',
            index=False
        )

    pd.DataFrame({
        'Parametro': [
            'Umbral_correlacion',
            'Metodo_correlacion',
            'Seed',
            'Uso_de_Etiqueta',
            'Variables_originales',
            'Variables_conservadas',
            'Variables_eliminadas'
        ],
        'Valor': [
            UMBRAL_CORRELACION,
            'Spearman absoluto',
            SEED,
            'NO',
            X.shape[1],
            len(variables_conservadas),
            len(variables_eliminadas)
        ]
    }).to_excel(
        writer,
        sheet_name='Configuracion',
        index=False
    )

print("\nDataset guardado en:")
print(ruta_salida)

print("\nRegistro guardado en:")
print(ruta_registro)
