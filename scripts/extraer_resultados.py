"""Build results/ from the saved outputs of the notebook and the tables of the memoria.

Nothing is recomputed: the notebook figures are parsed from the text that the
notebook printed in its original run, and the memoria figures are transcribed
from docs/Memoria.pdf (Tables 5.1-5.4). Every number in the output JSON carries
its source.

Usage (from the repository root):
    python scripts/extraer_resultados.py
"""
import base64
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebook" / "TFM_QNN.ipynb"
RESULTS = ROOT / "results"
FIGURES = ROOT / "docs" / "figures"

CONTACT_KEYS = ["P@L", "P@L/2", "P@L/5", "P@L/10", "R@L/5", "F1@L/5", "MCC", "Xd", "AUC-PR", "densidad"]
RANGE_NAMES = {"short (6-11)": "corto_6_11", "medium (12-23)": "medio_12_23", "long (>=24)": "largo_24"}


# ── Notebook output parsing ─────────────────────────────────────────────────
def cell_texts(nb):
    """Yield (cell, printed text) for every code cell with stream output."""
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        t = "".join("".join(o["text"]) for o in c.get("outputs", []) if "text" in o)
        if t:
            yield c, t


def find_output(nb, marker):
    for c, t in cell_texts(nb):
        if marker in t:
            return c, t
    raise LookupError(f"no saved output contains {marker!r}")


def parse_contacts(text):
    out = {}
    for blk in re.split(r"\n── ", text):
        head = blk.split(" ──")[0].strip()
        if not head.endswith("contactos"):
            continue
        name = head.replace(" — contactos", "")
        out[name] = {}
        row = r"^(short \(6-11\)|medium \(12-23\)|long \(>=24\))\s+" + r"\s+".join([r"([-\d.]+)"] * 10)
        for m in re.finditer(row, blk, re.M):
            out[name][RANGE_NAMES[m[1]]] = {k: float(m[i + 2]) for i, k in enumerate(CONTACT_KEYS)}
    return out


def parse_structure(text):
    out = {}
    for blk in re.split(r"\n── ", text):
        head = blk.split(" ──")[0].strip()
        if "estructura 3D" not in head:
            continue
        name = re.sub(r"\s*—\s*estructura 3D.*", "", head)
        g = lambda pat: float(re.search(pat, blk)[1])
        agg = {
            "RMSD_A": g(r"RMSD\s+:\s+([\d.]+)"),
            "GDT_TS": g(r"GDT_TS\s+:\s+([\d.]+)"), "GDT_TS_desv": g(r"GDT_TS\s+:\s+[\d.]+ ± ([\d.]+)"),
            "GDT_HA": g(r"GDT_HA\s+:\s+([\d.]+)"),
            "TM_score": g(r"TM-score:\s+([\d.]+)"), "TM_score_desv": g(r"TM-score:\s+[\d.]+ ± ([\d.]+)"),
            "lDDT": g(r"lDDT\s+:\s+([\d.]+)"),
            "GDT_TS_por_umbral_A": {c: float(v) for c, v in re.findall(r"<=\s+([\d.]+) A : ([\d.]+)", blk)},
            "n_proteinas": int(re.search(r"n=(\d+)", blk)[1]),
        }
        per = [{"id": m[1], "L": int(m[2]), "RMSD_A": float(m[3]), "GDT_TS": float(m[4]),
                "TM_score": float(m[5]), "lDDT": float(m[6])}
               for m in re.finditer(r"^\s{4}(\S+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$", blk, re.M)]
        out[name] = {"agregado": agg, "por_proteina": per}
    return out


def parse_history(text):
    rows = []
    pat = (r"^\s+(\d+)\s+\|\s+([\d.]+)\s+\|\s+([\d.]+)\s+\|\s+([\d.]+)\s+\|\s+([\d.]+)"
           r"\s+\|\s+([\d.e+-]+)\s+\|\s+([\d.e+-]+)\s+\|\s+([\d.]+)")
    for m in re.finditer(pat, text, re.M):
        rows.append({"epoca": int(m[1]), "loss_train": float(m[2]), "acc_train": float(m[3]),
                     "loss_val": float(m[4]), "acc_val": float(m[5]), "lr_clasico": float(m[6]),
                     "lr_cuantico": float(m[7]), "norma_grad_cuantico": float(m[8])})
    return rows


def parse_ablation_epochs(text):
    arms = {}
    for part in re.split(r"={70}\n", text):
        head = re.match(r"(Híbrido cuántico \(MERA\)|Baseline clásico \(Linear\))\s+\(([\d,]+) parámetros, ([\d,]+)", part)
        if head:
            current = head[1]
            arms[current] = {"parametros_totales": int(head[2].replace(",", "")),
                             "parametros_ruta_intercambiable": int(head[3].replace(",", "")), "epocas": []}
            continue
        if arms:
            for m in re.finditer(r"epoch\s+(\d+) \| train ([\d.]+)/([\d.]+) \| val ([\d.]+)/([\d.]+)", part):
                arms[current]["epocas"].append({"epoca": int(m[1]), "loss_train": float(m[2]), "acc_train": float(m[3]),
                                                "loss_val": float(m[4]), "acc_val": float(m[5])})
            stop = re.search(r"early stop en epoch (\d+)", part)
            if stop:
                arms[current]["parada_temprana_epoca"] = int(stop[1])
    return arms


# ── Memoria tables (docs/Memoria.pdf, chapter 5) ────────────────────────────
MEMORIA = {
    "fuente": "docs/Memoria.pdf, capítulo 5 (Tablas 5.1-5.4)",
    "contactos_tabla_5_1": {
        "descripcion": "224 proteínas del conjunto de validación oficial de ProteinNet CASP11; rangos exclusivos; umbral 8 Å",
        "sistema_propuesto": {
            "corto_6_11":  {"P@L": 0.875, "P@L/2": 0.885, "P@L/5": 0.889, "MCC": 0.101, "Xd": 4.36},
            "medio_12_23": {"P@L": 0.389, "P@L/2": 0.398, "P@L/5": 0.408, "MCC": 0.071, "Xd": 3.59},
            "largo_24":    {"P@L": 0.102, "P@L/2": 0.107, "P@L/5": 0.109, "MCC": 0.018, "Xd": 1.81},
        },
        "esm2_referencia": {
            "corto_6_11":  {"P@L": 0.697, "P@L/2": 0.700, "P@L/5": 0.699, "MCC": 0.018, "Xd": 0.79},
            "medio_12_23": {"P@L": 0.250, "P@L/2": 0.250, "P@L/5": 0.250, "MCC": 0.009, "Xd": 0.69},
            "largo_24":    {"P@L": 0.086, "P@L/2": 0.087, "P@L/5": 0.089, "MCC": 0.007, "Xd": 0.99},
        },
        "densidad_contactos": {"corto_6_11": 0.655, "medio_12_23": 0.224, "largo_24": 0.062},
        "mejora_sobre_esm2_puntos_P@L/5": {"corto_6_11": 19.0, "medio_12_23": 15.8, "largo_24": 2.1},
    },
    "estructura_3d_tabla_5_2": {
        "descripcion": "30 proteínas del conjunto de validación oficial de ProteinNet CASP11",
        "media": {"RMSD_A": 14.24, "GDT_TS": 0.114, "GDT_HA": 0.028, "TM_score": 0.222, "lDDT": 0.363},
        "desviacion": {"GDT_TS": 0.111, "TM_score": 0.094},
        "mejor_caso": {"RMSD_A": 3.55, "GDT_TS": 0.485, "TM_score": 0.425, "lDDT": 0.542},
        "peor_caso": {"RMSD_A": 33.90, "GDT_TS": 0.000, "TM_score": 0.003, "lDDT": 0.260},
        "notas": "Mejor caso: cadena de 50 residuos (2KJI). En 2 de 30 proteínas la reconstrucción es degenerada (GDT_TS 0, RMSD > 24 Å).",
    },
    "casp_tabla_5_3": {
        "metrica": "P@L/5, contactos de largo alcance (>= 24)",
        "CONSIP2_MetaPSICOV_CASP11": {"P@L/5": 0.270, "usa_MSA": True},
        "mejor_grupo_CASP10": {"P@L/5": 0.20, "usa_MSA": True, "nota": "aproximado, sin covariación"},
        "este_trabajo": {"P@L/5": 0.109, "usa_MSA": False},
        "esm2_referencia": {"P@L/5": 0.089, "usa_MSA": False},
        "predictor_aleatorio": {"P@L/5": 0.062},
        "nota": "CASP evalúa dominios de modelado libre; aquí se evalúan todas las proteínas. Comparación orientativa.",
    },
    "ablacion_tabla_5_4": {
        "metrica": "P@L/5 largo alcance (MERA / capa lineal) y TM-score (MERA / lineal)",
        "replica_1_training_30":  {"MERA": 0.1047, "lineal": 0.1050, "diferencia": -0.0003, "TM_MERA": 0.227, "TM_lineal": 0.232},
        "replica_2_training_100": {"MERA": 0.0980, "lineal": 0.1051, "diferencia": -0.0071, "TM_MERA": 0.229, "TM_lineal": 0.223},
        "parametros_ruta_intercambiable": {"MERA": 312, "lineal": 351},
        "parametros_totales": {"MERA": 45103, "lineal": 45142},
        "conclusion": "El circuito cuántico no proporciona ventaja medible sobre un componente clásico de capacidad equivalente.",
    },
    "gradiente_cuantico": "La norma del gradiente de los parámetros cuánticos desciende de ~0,22 en las primeras épocas a ~0,015 en las últimas.",
}


def main():
    nb = json.load(open(NOTEBOOK, encoding="utf-8"))

    _, t_cfg = find_output(nb, "Config activa:")
    _, t_train = find_output(nb, "Warmup cuántico")
    _, t_eval = find_output(nb, "Modelo híbrido — contactos")
    _, t_abl = find_output(nb, "¿APORTA ALGO EL CIRCUITO CUÁNTICO?")
    _, t_data = find_output(nb, "Input dim")
    c_diag, t_diag = find_output(nb, "Mejor epoch:")

    contacts = {**parse_contacts(t_eval), **parse_contacts(t_abl)}
    structure = {**parse_structure(t_eval), **parse_structure(t_abl)}
    history = parse_history(t_train)
    ablation = parse_ablation_epochs(t_abl)

    run = {
        "fuente": "salidas guardadas de notebook/TFM_QNN.ipynb (ejecución original)",
        "corresponde_a": "réplica 2 del estudio de ablación de la memoria (training_100)",
        "configuracion": {
            "dataset": "ProteinNet CASP11", "training_set": "training_100",
            "proteinas_muestreadas": int(re.search(r"muestreo aleatorio: (\d+)", find_output(nb, "muestreo aleatorio")[1])[1]),
            "proteinas_disponibles_en_fichero": 87573,
            "particion": "80 % entrenamiento / 20 % monitorización, por proteína completa",
            "pares_por_intervalo_y_particion": 20000,
            "pares_entrenamiento": int(re.search(r"Train pares : (\d+)", t_data)[1]),
            "pares_monitorizacion": int(re.search(r"Val pares   : (\d+)", t_data)[1]),
            "dimension_entrada": int(re.search(r"Input dim\s+: (\d+)D", t_data)[1]),
            "batch": 64, "epocas_maximas": 120, "paciencia": 10,
            "dropout": 0.5, "weight_decay": 0.01, "lr_clasico": 1e-3, "lr_cuantico": 0.02,
            "warmup_cuantico_epocas": 3, "semilla": 42,
            "evaluacion_contactos_proteinas": 224, "evaluacion_3d_proteinas": 30,
            "modelo_lenguaje": "ESM-2 t12 35M UR50D (capa 6 + atención 12×20)",
            "gpu": "NVIDIA GeForce RTX 5070 Ti",
        },
        "arquitectura": {
            "parametros_totales": 45103, "parametros_embudo_mlp": 38924, "parametros_circuito": 312,
            "circuito": {"qubits": 12, "niveles": 4, "bloques": 27, "parametros_por_bloque": 8,
                         "parametros_bloques": 216, "parametros_recarga": 96,
                         "parametros_recarga_activos": 46,
                         "puertas_bloque": "U3 ⊗ U3 + RYY·RZZ", "inicializacion": "U(-0.05, 0.05)",
                         "observables": "12 <Z> + 9 <ZZ> + 3 <X> + 3 <Y> = 27"},
        },
        "entrenamiento": {"historial": history,
                          "mejor_epoca": int(re.search(r"Mejor epoch: (\d+)", t_diag)[1]) + 1,
                          "mejor_loss_val": float(re.search(r"Mejor val loss: ([\d.]+)", t_train)[1]),
                          "parada_temprana_epoca": int(re.search(r"Early stop en epoch (\d+)", t_train)[1])},
        "contactos": contacts,
        "estructura_3d": structure,
        "ablacion": {
            **{k: v for k, v in ablation.items()},
            "resumen": {
                "P@L/5_largo_MERA": float(re.search(r"cuántico ([\d.]+) \| clásico", t_abl)[1]),
                "P@L/5_largo_lineal": float(re.search(r"clásico ([\d.]+) \| diferencia", t_abl)[1]),
                "diferencia": float(re.search(r"diferencia ([-+\d.]+)", t_abl)[1]),
                "TM_MERA": float(re.search(r"TM-score\s+— cuántico ([\d.]+)", t_abl)[1]),
                "TM_lineal": float(re.search(r"TM-score\s+— cuántico [\d.]+ \| clásico ([\d.]+)", t_abl)[1]),
            },
        },
    }

    data = {
        "schema_version": "2.0",
        "proyecto": {
            "titulo": "Red neuronal cuántica híbrida para la predicción de estructura tridimensional de proteínas mediante embeddings de lenguaje proteico",
            "autor": "Marco Antonio Roca Rodríguez", "director": "Mariano Caruso",
            "tipo": "Trabajo Fin de Máster", "titulacion": "Máster Universitario en Computación Cuántica (UNIR)",
            "anio": 2026, "repositorio": "https://github.com/marrocrod/qnn-protein_structure-prediction",
        },
        "como_leer": (
            "Dos bloques de resultados con fuentes distintas. 'resultados_memoria' son las cifras publicadas "
            "en la memoria (ejecución principal y estudio de ablación). 'ejecucion_notebook' son las cifras que "
            "imprimió el notebook en su ejecución guardada, que es la réplica 2 de la ablación. Las métricas "
            "de contacto son fracciones (0-1); RMSD en Å; AUC-PR es el área bajo la curva precisión-recall."
        ),
        "resultados_memoria": MEMORIA,
        "ejecucion_notebook": run,
        "referencias_casp_notebook": {
            "metrica": "P@L/5 largo alcance del mejor grupo, con MSA",
            "CASP11_CONSIP2": 0.27, "CASP12": 0.47, "CASP13": 0.70, "CASP14": 0.82,
        },
    }
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "resultados_tfm.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ── Tidy CSV tables ─────────────────────────────────────────────────────
    with open(RESULTS / "metricas_contactos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fuente", "modelo", "rango"] + CONTACT_KEYS)
        for model, ranges in contacts.items():
            for rng, v in ranges.items():
                w.writerow(["notebook (réplica 2)", model, rng] + [v[k] for k in CONTACT_KEYS])
        t51 = MEMORIA["contactos_tabla_5_1"]
        for model, key in (("Sistema propuesto", "sistema_propuesto"), ("ESM-2 (referencia)", "esm2_referencia")):
            for rng, v in t51[key].items():
                w.writerow(["memoria (Tabla 5.1)", model, rng] + [v.get(k, "") for k in CONTACT_KEYS[:4]]
                           + ["", "", v["MCC"], v["Xd"], "", t51["densidad_contactos"][rng]])

    with open(RESULTS / "estructura_3d_por_proteina.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["modelo", "id", "L", "RMSD_A", "GDT_TS", "TM_score", "lDDT"])
        for model, d in structure.items():
            for r in d["por_proteina"]:
                w.writerow([model, r["id"], r["L"], r["RMSD_A"], r["GDT_TS"], r["TM_score"], r["lDDT"]])

    with open(RESULTS / "historial_entrenamiento.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(history[0]))
        w.writeheader()
        w.writerows(history)

    # Training-curves figure exactly as the notebook drew it
    FIGURES.mkdir(parents=True, exist_ok=True)
    for o in c_diag.get("outputs", []):
        if "image/png" in o.get("data", {}):
            (FIGURES / "entrenamiento_notebook.png").write_bytes(base64.b64decode(o["data"]["image/png"]))

    print(f"Modelos con métricas de contacto : {list(contacts)}")
    print(f"Modelos con métricas 3D          : {list(structure)}")
    print(f"Épocas de entrenamiento          : {len(history)}")
    print("Escrito: results/resultados_tfm.json, metricas_contactos.csv, "
          "estructura_3d_por_proteina.csv, historial_entrenamiento.csv, docs/figures/entrenamiento_notebook.png")


if __name__ == "__main__":
    main()
