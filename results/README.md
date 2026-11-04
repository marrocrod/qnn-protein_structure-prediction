# Resultados

Todo lo que hay en esta carpeta se genera con [`scripts/extraer_resultados.py`](../scripts/extraer_resultados.py) **sin recalcular nada**. Hay dos fuentes y cada cifra indica de cuál procede:

| Fuente | Qué es | Dónde aparece |
|---|---|---|
| **Memoria** | Cifras publicadas en [`docs/Memoria.pdf`](../docs/Memoria.pdf), capítulo 5 (Tablas 5.1–5.4): ejecución principal y estudio de ablación con sus dos réplicas | `resultados_memoria` en el JSON; filas `memoria (Tabla 5.1)` del CSV de contactos |
| **Notebook** | Salidas guardadas en [`notebook/TFM_QNN.ipynb`](../notebook/TFM_QNN.ipynb). Es la **réplica 2** de la ablación (`training_100`, 5 000 proteínas) | `ejecucion_notebook` en el JSON; resto de CSV |

## Ficheros

| Fichero | Contenido |
|---|---|
| [`resultados_tfm.json`](resultados_tfm.json) | Resumen completo: configuración, arquitectura, historial de entrenamiento, métricas de contacto y 3D, ablación y referencias de CASP |
| [`metricas_contactos.csv`](metricas_contactos.csv) | P@L, P@L/2, P@L/5, P@L/10, R@L/5, F1@L/5, MCC, Xd, AUC-PR y densidad por modelo y rango |
| [`estructura_3d_por_proteina.csv`](estructura_3d_por_proteina.csv) | RMSD, GDT_TS, TM-score y lDDT de las 30 proteínas, para el modelo principal y los dos brazos de la ablación |
| [`historial_entrenamiento.csv`](historial_entrenamiento.csv) | Pérdida, acierto, tasas de aprendizaje y norma del gradiente cuántico por época |
| [`pymol/`](pymol/) | Figura de la reconstrucción 3D y script para generarla |

Cuando se ejecuta, el notebook escribe además `registro_ejecuciones.json`: el registro en bruto que leen las tablas de la Parte VII. No se versiona.

## Cifras principales

**Contactos (memoria, Tabla 5.1) — P@L/5 sobre 224 proteínas de CASP11**

| Rango | Sistema propuesto | ESM-2 nativo | Azar | Mejora sobre ESM-2 |
|---|---:|---:|---:|---:|
| Corto (6–11) | **88,9 %** | 69,9 % | 65,5 % | +19,0 |
| Medio (12–23) | **40,8 %** | 25,0 % | 22,4 % | +15,8 |
| Largo (≥ 24) | **10,9 %** | 8,9 % | 6,2 % | +2,1 |

**Estructura 3D (memoria, Tabla 5.2) — media de 30 proteínas:** TM-score 0,222 · GDT_TS 0,114 · RMSD 14,24 Å · lDDT 0,363.

**Ablación (memoria, Tabla 5.4) — P@L/5 de largo alcance**

| Réplica | Circuito MERA | Capa lineal | Diferencia |
|---|---:|---:|---:|
| 1 · `training_30` | 0,1047 | 0,1050 | −0,0003 |
| 2 · `training_100` (notebook) | 0,0980 | 0,1051 | −0,0071 |

## Unidades y convenciones

- Las métricas de contacto están en tanto por uno en el JSON y en los CSV (0,109 = 10,9 %).
- RMSD en Å; GDT_TS, GDT_HA, TM-score y lDDT entre 0 y 1.
- Los rangos son exclusivos por separación en la secuencia $|i-j|$: `corto_6_11`, `medio_12_23` y `largo_24` (≥ 24).
- AUC-PR es el área bajo la curva precisión-*recall*, no la ROC.
