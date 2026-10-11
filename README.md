# QNN Protein Structure Prediction

**Red Neuronal Cuántica Híbrida para la Predicción de Estructura de Proteínas**  
Marco Antonio Roca Rodríguez · Trabajo de Fin de Máster · Máster Universitario en Computación Cuántica (UNIR)  
Director: Mariano Caruso

Repositorio del TFM: https://github.com/marrocrod/qnn-protein_structure-prediction

Este proyecto estudia un modelo híbrido clásico-cuántico para la predicción de contactos entre residuos y la reconstrucción aproximada de estructuras tridimensionales de proteínas. El notebook combina representaciones de ESM-2 con una capa cuántica basada en MERA y compara su comportamiento con una ablación clásica.

> **Estado de los resultados:** el JSON conserva los resultados de una ejecución anterior (5.000 proteínas y 100.000 pares) como referencia histórica. El notebook de este repositorio está configurado para la corrida objetivo `training_100`, 15.000 proteínas y 200.000 pares, pero se han eliminado sus salidas guardadas para evitar confundir métricas antiguas con resultados de esa corrida. No se han proporcionado todavía los resultados numéricos de la corrida final ni de sus dos réplicas; el JSON los deja explícitamente pendientes.

## Estructura

```text
qnn-protein_structure-prediction/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── notebook/
│   └── TFM_QNN.ipynb
├── results/
│   ├── resultados_tfm.json
│   └── pymol/
│       └── README.md
├── docs/
│   └── README.md
└── experiments/
    ├── README.md
    └── model_2d/
        └── README.md
```

## Requisitos

- Python 3.10 o superior.
- GPU NVIDIA con CUDA recomendada para la ejecución completa. La compatibilidad depende de la versión de PyTorch instalada.
- Espacio de disco para ProteinNet y la caché de ESM-2; el tamaño total depende de los subconjuntos y artefactos descargados.

Instala las dependencias generales:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Instala PyTorch con la variante adecuada para tu plataforma/GPU siguiendo https://pytorch.org/get-started/locally/. Después, comprueba `torch.cuda.is_available()`.

## Datos

El notebook utiliza **ProteinNet CASP11**, que no se incluye en este repositorio. Descarga los datos desde https://github.com/aqlaboratory/proteinnet y coloca los ficheros en `casp11/` al nivel raíz del repositorio:

```text
qnn-protein_structure-prediction/
├── casp11/
│   ├── training_100
│   └── validation
└── notebook/
    └── TFM_QNN.ipynb
```

El notebook busca esos datos mediante rutas relativas desde `notebook/`. No subas los ficheros de ProteinNet al repositorio.

## Configuración de la corrida objetivo

En el bloque de configuración del notebook:

| Parámetro | Valor objetivo |
|---|---:|
| `TRAINING_SET` | `training_100` |
| `MAX_PROTEINS_TRAIN` | `15000` |
| `MAX_PER_BIN` | `40000` |
| Pares objetivo | `200000` (5 bins × 40.000) |
| `N_EVAL_CONTACT` | `224` |
| `N_EVAL_3D` | `30` |

Haz primero una ejecución de prueba con `RUN_MODE = "smoke"`. Para la corrida completa usa `RUN_MODE = "full"`. Ejecuta las celdas en orden y conserva el JSON generado, los logs y la configuración exacta de cada réplica.

## Resultados

`results/resultados_tfm.json` organiza los resultados por corrida y separa la corrida final de las réplicas. La sección `ejecucion_anterior_no_final` documenta métricas existentes de una configuración previa; **no debe citarse como resultado de la corrida final**. Completa los campos `pendiente` de `corrida_final` y `replicas` con los resultados realmente medidos, incluyendo semillas, configuración, métricas y fecha de ejecución.

Los resultados anteriores muestran diferencias pequeñas entre la variante cuántica y la capa lineal en varias métricas; por tanto, no justifican afirmar una ventaja cuántica concluyente. Las comparaciones con cifras CASP basadas en MSA tampoco son estrictamente homogéneas con una inferencia de secuencia individual.

## Estructuras PDB y PyMOL

Los ejemplos PDB y la imagen de la figura del caso no estaban entre los archivos proporcionados al preparar este esqueleto. Añade únicamente artefactos que puedas redistribuir y documenta para cada estructura si es referencia real, predicción o estructura refinada. Consulta `results/pymol/README.md`.

## Documentación del TFM

Copia `memoria.pdf`, `memoria_latex.zip` y `paper_tfm.pdf`/`paper_tfm.tex` en `docs/`. Consulta `docs/README.md` para mantener la documentación organizada.

## Experimentos exploratorios

Los experimentos no usados como corrida principal van en `experiments/`, con sus propios parámetros, semillas, dependencias y conclusiones. `experiments/model_2d/` está preparado como carpeta inicial.

## Reproducibilidad y limitaciones

- Fija y registra las semillas de cada corrida y réplica.
- Registra versiones de Python, PyTorch, PennyLane, ESM y CUDA.
- No incluyas checkpoints grandes, cachés de modelos, datos ProteinNet ni entornos virtuales en Git.
- Distingue siempre métricas de validación, métricas de test y resultados exploratorios.
- La licencia de este repositorio se aplica al código propio; no reemplaza las licencias/condiciones de ProteinNet, ESM-2 ni de otras dependencias.

## Cita

Si utilizas este trabajo, cita el TFM y la versión concreta del repositorio. Completa la referencia bibliográfica cuando el paper esté incorporado en `docs/`.
