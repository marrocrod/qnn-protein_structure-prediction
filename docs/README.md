# Documentación

| Documento | Descripción |
|---|---|
| [`Memoria.pdf`](Memoria.pdf) | Memoria completa del TFM (91 páginas): contexto, estado del arte, metodología, resultados y conclusiones |
| [`paper_TFM.pdf`](paper_TFM.pdf) | Artículo derivado (4 páginas, en inglés): *Does the Quantum Circuit Help? A Controlled Ablation of a Hybrid Quantum-Classical Protein Contact Predictor* |
| [`presentacion_defensa.pdf`](presentacion_defensa.pdf) | Diapositivas de la defensa (21 páginas) |
| [`arquitectura.md`](arquitectura.md) | Descripción técnica del sistema tal y como está implementado en el notebook: datos, vector de par, MERA, entrenamiento, evaluación y ablación |
| [`figures/`](figures/) | Figuras del README, generadas con [`scripts/generar_figuras.py`](../scripts/generar_figuras.py) a partir de `results/resultados_tfm.json` |

## Figuras

| Fichero | Contenido |
|---|---|
| `arquitectura.png` | Flujo completo: secuencia → ESM-2 → vector de par → embudo → MERA → capas clásicas → distancias → estructura 3D |
| `circuito_mera.png` | Los 4 niveles y 27 bloques del circuito, con la recarga de datos y la medición |
| `contactos.png` | P@L/5 por rango: sistema propuesto, ESM-2 nativo y azar (memoria, Tabla 5.1) |
| `ablacion.png` | Circuito MERA frente a capa lineal en las dos réplicas (memoria, Tabla 5.4) |
| `casp11.png` | Contexto frente a CASP11 (memoria, Tabla 5.3) |
| `gradiente_cuantico.png` | Norma del gradiente del circuito y pérdida de monitorización por época (ejecución del notebook) |
| `estructura_vs_longitud.png` | GDT_TS de las 30 proteínas frente a su longitud (ejecución del notebook) |
| `entrenamiento_notebook.png` | Curvas de entrenamiento tal y como las dibujó el notebook |
