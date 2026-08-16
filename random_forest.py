import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

NUM_RONDAS = 10
NUM_PERMUTACIONES = 200
RONDAS_POR_PERMUTACION = 5

ruta_dataset = '/content/drive/MyDrive/Canciones proyecto voam/dataset_final_para_modelo.xlsx'
df = pd.read_excel(ruta_dataset)

df_voam = df[df['Etiqueta'] == 1]
df_control = df[df['Etiqueta'] == 0]

n_voam = len(df_voam)

variables = df.drop(
    columns=['Nombre_Archivo', 'Etiqueta']
).columns

importancias_acumuladas = pd.DataFrame(index=variables)


def crear_rf(seed):
    return RandomForestClassifier(
        n_estimators=300,
        max_features=0.33,
        max_depth=7,
        min_samples_leaf=1,
        oob_score=True,
        random_state=seed
    )


def evaluar_ronda(df_ronda, seed):

    X = df_ronda.drop(
        columns=['Nombre_Archivo', 'Etiqueta']
    )

    y = df_ronda['Etiqueta']

    rf = crear_rf(seed)
    rf.fit(X, y)

    accuracy = rf.oob_score_

    oob_probs = rf.oob_decision_function_[:, 1]
    validas = ~np.isnan(oob_probs)

    auc = roc_auc_score(
        y[validas],
        oob_probs[validas]
    )

    return accuracy, auc, rf.feature_importances_


print(
    f"Procesando {NUM_RONDAS} rondas "
    f"(Voam: {n_voam}, Control: {n_voam})"
)

precisiones = []
aucs = []

for i in range(NUM_RONDAS):

    control_muestra = df_control.sample(
        n=n_voam,
        random_state=i
    )

    df_ronda = pd.concat(
        [df_voam, control_muestra]
    ).sample(
        frac=1,
        random_state=i
    )

    accuracy, auc, importancias = evaluar_ronda(
        df_ronda,
        seed=i
    )

    precisiones.append(accuracy)
    aucs.append(auc)

    importancias_acumuladas[f'Ronda_{i+1}'] = importancias

    print(
        f"Ronda {i+1}/{NUM_RONDAS} -> "
        f"Accuracy: {accuracy:.2%} | AUC: {auc:.3f}"
    )


precisiones = np.array(precisiones)
aucs = np.array(aucs)

print(
    f"\nAccuracy promedio: {precisiones.mean():.2%} "
    f"(rango: {precisiones.min():.2%} - {precisiones.max():.2%})"
)

print(
    f"AUC promedio: {aucs.mean():.3f} "
    f"(rango: {aucs.min():.3f} - {aucs.max():.3f})"
)

importancias_acumuladas['Importancia_Media'] = (
    importancias_acumuladas.mean(axis=1)
)

importancias_acumuladas['Desviacion_Estandar'] = (
    importancias_acumuladas
    .drop(columns=['Importancia_Media'])
    .std(axis=1)
)

ranking_final = importancias_acumuladas.sort_values(
    by='Importancia_Media',
    ascending=False
)

ruta_ranking = (
    '/content/drive/MyDrive/Canciones proyecto voam/'
    'ranking_variables_gini.xlsx'
)

ranking_final.to_excel(
    ruta_ranking,
    index=True
)

print("\nTOP 10 VARIABLES")

top_10 = (
    ranking_final[
        ['Importancia_Media', 'Desviacion_Estandar']
    ].head(10) * 100
)

print(
    top_10.round(2).astype(str) + " %"
)


print(
    f"\nIniciando {NUM_PERMUTACIONES} permutaciones..."
)

accuracy_observada = precisiones.mean()
auc_observado = aucs.mean()

acc_nulas = []
auc_nulas = []

df_base = pd.concat(
    [df_voam, df_control]
).reset_index(drop=True)


for p in range(NUM_PERMUTACIONES):

    df_permutado = df_base.copy()

    df_permutado['Etiqueta'] = (
        df_base['Etiqueta']
        .sample(
            frac=1,
            random_state=1000 + p
        )
        .values
    )

    df_voam_perm = df_permutado[
        df_permutado['Etiqueta'] == 1
    ]

    df_control_perm = df_permutado[
        df_permutado['Etiqueta'] == 0
    ]

    n_perm = len(df_voam_perm)

    accs_p = []
    aucs_p = []

    for r in range(RONDAS_POR_PERMUTACION):

        seed = p * 100 + r

        control_muestra = df_control_perm.sample(
            n=n_perm,
            random_state=seed
        )

        df_ronda_p = pd.concat(
            [df_voam_perm, control_muestra]
        ).sample(
            frac=1,
            random_state=seed
        )

        acc_p, auc_p, _ = evaluar_ronda(
            df_ronda_p,
            seed=seed
        )

        accs_p.append(acc_p)
        aucs_p.append(auc_p)

    acc_nulas.append(np.mean(accs_p))
    auc_nulas.append(np.mean(aucs_p))

    if (p + 1) % 50 == 0:
        print(
            f"{p + 1}/{NUM_PERMUTACIONES} "
            "permutaciones"
        )


acc_nulas = np.array(acc_nulas)
auc_nulas = np.array(auc_nulas)

p_valor_acc = (
    (np.sum(acc_nulas >= accuracy_observada) + 1)
    / (NUM_PERMUTACIONES + 1)
)

p_valor_auc = (
    (np.sum(auc_nulas >= auc_observado) + 1)
    / (NUM_PERMUTACIONES + 1)
)


print("\nRESULTADO DEL TEST DE PERMUTACIÓN")

print(
    f"Accuracy observada: {accuracy_observada:.2%}"
)

print(
    f"Accuracy nula: {acc_nulas.mean():.2%}"
)

print(
    f"p-valor Accuracy: {p_valor_acc:.4f}"
)

print(
    f"\nAUC observado: {auc_observado:.3f}"
)

print(
    f"AUC nulo: {auc_nulas.mean():.3f}"
)

print(
    f"p-valor AUC: {p_valor_auc:.4f}"
)
