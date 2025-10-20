# ==========================================
# visualize_defense_clusters.py
# ISAC 2025 – Club América | Liga MX
# Radar charts de perfiles defensivos
# ==========================================
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# ==========================================
# CONFIGURACIÓN
# ==========================================
DATA_DIR = "../data"
TEAM = "América"

# Cargar el archivo generado por build_defense_clusters.py
file_path = os.path.join(DATA_DIR, f"{TEAM.replace(' ', '_')}_defense_clusters.csv")
if not os.path.exists(file_path):
    raise FileNotFoundError(f"No se encontró el archivo {file_path}. Corre primero build_defense_clusters.py")

df = pd.read_csv(file_path)

# ==========================================
# VARIABLES A INCLUIR EN EL RADAR
# ==========================================
features = [
    "tackles_90",
    "interceptions_90",
    "clearance_90",
    "pressures_90",
    "ball_recoveries_90",
    "aerial_ratio",
    "aerial_wins_90",
    "def_action_regains_90",
    "fhalf_pressures_ratio",
    "forward_pass_proportion",
    "passing_ratio",
    "long_ball_ratio",
    "dribble_faced_ratio"
]

# Calcular promedios por clúster
cluster_means = df.groupby("cluster")[features].mean().reset_index()

# Normalizar (para que todos los ejes sean comparables)
cluster_norm = cluster_means.copy()
for c in features:
    max_val = df[c].max()
    min_val = df[c].min()
    cluster_norm[c] = (cluster_means[c] - min_val) / (max_val - min_val)

# ==========================================
# RADAR CHART
# ==========================================
def make_radar(values, categories, title, color):
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    values = values.tolist()
    values += values[:1]  # cerrar el polígono
    angles += angles[:1]

    plt.polar(angles, values, color=color, linewidth=2, linestyle='solid')
    plt.fill(angles, values, color=color, alpha=0.25)
    plt.xticks(angles[:-1], categories, color='grey', size=8)
    plt.title(title, size=13, color=color, y=1.1)

# ==========================================
# PLOTEAR TODOS LOS CLÚSTERES
# ==========================================
colors = plt.cm.tab10.colors
n_clusters = cluster_norm["cluster"].nunique()

plt.figure(figsize=(10, 10))
for i in range(n_clusters):
    plt.subplot(3, 2, i+1, polar=True)
    make_radar(
        cluster_norm.loc[i, features],
        features,
        f"Cluster {int(cluster_norm.loc[i, 'cluster'])}",
        color=colors[i % 10]
    )

plt.tight_layout()
plt.suptitle(f"Perfiles Defensivos - {TEAM} (Liga MX 2024/25)", y=1.05, fontsize=16)
plt.show()

# ==========================================
# OPCIONAL: GUARDAR IMAGEN
# ==========================================
out_path = os.path.join(DATA_DIR, f"{TEAM.replace(' ', '_')}_defense_clusters_radar.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"✅ Radar charts guardados en: {out_path}")
