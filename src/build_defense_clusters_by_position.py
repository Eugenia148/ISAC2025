# ==========================================
# build_defense_clusters_by_position.py
# ISAC 2025 – Club América | Liga MX
# Genera métricas defensivas y radar charts por posición
# ==========================================
import os
import ast
import math
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from statsbombpy import sb
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from math import pi

np.random.seed(42)

# ==========================================
# CONFIGURACIÓN
# ==========================================
DATA_DIR   = "../data"
TEAM       = "América"
COMP_ID    = 108
SEASON_ID  = 506
N_CLUSTERS = 5

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def get_start_x(row):
    loc = row.get("location", None)
    return loc[0] if isinstance(loc, list) and len(loc) > 0 else np.nan

def get_end_x(row):
    try:
        end = row["pass"].get("end_location", None)
        return end[0] if isinstance(end, list) and len(end) > 0 else np.nan
    except: return np.nan

def pass_length(row):
    try:
        loc = row["location"]; end = row["pass"]["end_location"]
        return math.hypot(end[0]-loc[0], end[1]-loc[1])
    except: return np.nan

def is_completed_pass(row):
    try: return row["pass"].get("outcome") is None
    except: return False

def is_event(row, name):
    t = row.get("type", None)
    if isinstance(t, dict) and "name" in t:
        return t["name"] == name
    if isinstance(t, str):
        return t == name
    return False

def is_duel_event(x):
    t = x.get("type", None)
    if isinstance(t, dict):
        return t.get("name") == "Duel"
    elif isinstance(t, str):
        return t == "Duel"
    return False

def is_aerial_duel(x):
    if not is_duel_event(x):
        return False
    duel_type = x.get("duel", {}).get("type", {})
    return "Aerial" in str(duel_type)

def is_aerial_won(x):
    if not is_duel_event(x):
        return False
    duel_outcome = x.get("duel", {}).get("outcome", {})
    return duel_outcome.get("name") == "Won"

# ==========================================
# RADAR CHART
# ==========================================
def make_radar(values, categories, title, color, output_path):
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    values = values.tolist()
    values += values[:1]
    angles += angles[:1]

    plt.figure(figsize=(6,6))
    plt.polar(angles, values, color=color, linewidth=2)
    plt.fill(angles, values, color=color, alpha=0.25)
    plt.xticks(angles[:-1], categories, color='grey', size=8)
    plt.title(title, size=13, color=color, y=1.1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"📊 Radar chart guardado en: {output_path}")

# ==========================================
# PIPELINE PARA CADA POSICIÓN
# ==========================================
def process_defenders(df, position_filter, label_suffix):
    """Filtra por tipo de defensor, calcula métricas, clusteriza y genera radar."""
    df_pos = df[df["position"].isin(position_filter)].copy()
    if df_pos.empty:
        print(f"⚠️ No se encontraron jugadores para {label_suffix}.")
        return

    print(f"\n🔹 Analizando: {label_suffix}")
    print(f"   Jugadores: {df_pos['player'].nunique()} | Eventos: {len(df_pos)}")

    # --- Variables defensivas ---
    df_pos["start_x"] = df_pos.apply(get_start_x, axis=1)
    df_pos["end_x"]   = df_pos.apply(get_end_x, axis=1)
    df_pos["pass_len"] = df_pos.apply(pass_length, axis=1)
    df_pos["pass_completed"] = df_pos.apply(is_completed_pass, axis=1)

    df_pos["is_tackle"]       = df_pos.apply(lambda x: is_event(x,"Tackle"), axis=1)
    df_pos["is_interception"] = df_pos.apply(lambda x: is_event(x,"Interception"), axis=1)
    df_pos["is_clearance"]    = df_pos.apply(lambda x: is_event(x,"Clearance"), axis=1)
    df_pos["is_pressure"]     = df_pos.apply(lambda x: is_event(x,"Pressure"), axis=1)
    df_pos["is_recovery"]     = df_pos.apply(lambda x: is_event(x,"Ball Recovery"), axis=1)
    df_pos["is_dribbled_past"]= df_pos.apply(lambda x: is_event(x,"Dribbled Past"), axis=1)
    df_pos["is_aerial"]       = df_pos.apply(is_aerial_duel, axis=1)
    df_pos["aerial_won"]      = df_pos.apply(is_aerial_won, axis=1)

    df_pos["fhalf_pressure"]  = df_pos["is_pressure"] & (df_pos["start_x"]>60)
    df_pos["forward_pass"]    = (df_pos["pass_len"].notna()) & (df_pos["end_x"]>df_pos["start_x"])
    df_pos["long_ball"]       = df_pos["pass_len"]>30
    df_pos["long_ball_completed"] = df_pos["long_ball"] & df_pos["pass_completed"]

    # --- Agregación ---
    agg = df_pos.groupby(["player_id","player"]).agg(
        tackles=("is_tackle","sum"),
        interceptions=("is_interception","sum"),
        clearances=("is_clearance","sum"),
        pressures=("is_pressure","sum"),
        fhalf_pressures=("fhalf_pressure","sum"),
        recoveries=("is_recovery","sum"),
        dribbled_past=("is_dribbled_past","sum"),
        aerials=("is_aerial","sum"),
        aerials_won=("aerial_won","sum"),
        forward_passes=("forward_pass","sum"),
        passes=("pass_len","count"),
        passes_completed=("pass_completed","sum"),
        long_balls=("long_ball","sum"),
        long_balls_completed=("long_ball_completed","sum"),
        avg_x_def_action=("start_x", lambda s: np.nanmean(
            df_pos.loc[s.index, "start_x"][
                df_pos.loc[s.index,"is_tackle"] | df_pos.loc[s.index,"is_interception"]
            ]
        )),
        avg_x_pressure=("start_x", lambda s: np.nanmean(
            df_pos.loc[s.index,"start_x"][df_pos.loc[s.index,"is_pressure"]]
        ))
    ).reset_index()

    agg["minutes"] = 900
    m = agg["minutes"].replace({0:np.nan})

    # --- Métricas por 90 y ratios ---
    agg["tackles_90"]       = agg["tackles"]/m*90
    agg["interceptions_90"] = agg["interceptions"]/m*90
    agg["clearance_90"]     = agg["clearances"]/m*90
    agg["pressures_90"]     = agg["pressures"]/m*90
    agg["ball_recoveries_90"]= agg["recoveries"]/m*90
    agg["dribbled_past_90"] = agg["dribbled_past"]/m*90
    agg["aerial_ratio"]     = agg["aerials_won"]/agg["aerials"].replace({0:np.nan})
    agg["aerial_wins_90"]   = agg["aerials_won"]/m*90
    agg["def_action_regains_90"] = (agg["recoveries"]+agg["interceptions"]+agg["tackles"])/m*90
    agg["fhalf_pressures_ratio"] = agg["fhalf_pressures"]/agg["pressures"].replace({0:np.nan})
    agg["forward_pass_proportion"] = agg["forward_passes"]/agg["passes"].replace({0:np.nan})
    agg["passing_ratio"]    = agg["passes_completed"]/agg["passes"].replace({0:np.nan})
    agg["long_ball_ratio"]  = agg["long_balls_completed"]/agg["long_balls"].replace({0:np.nan})
    agg["dribble_faced_ratio"] = 1 - (agg["dribbled_past"]/ (agg["tackles"]+agg["dribbled_past"]).replace({0:np.nan}))

    # --- Clustering ---
    features = [
        "tackles_90","interceptions_90","clearance_90","pressures_90",
        "ball_recoveries_90","aerial_ratio","aerial_wins_90",
        "def_action_regains_90","fhalf_pressures_ratio",
        "forward_pass_proportion","passing_ratio","long_ball_ratio",
        "dribble_faced_ratio","avg_x_def_action","avg_x_pressure"
    ]
    X = agg[features].fillna(0)
    scaler = StandardScaler()
    Xz = scaler.fit_transform(X)
    pca = PCA(n_components=2, random_state=42)
    Z = pca.fit_transform(Xz)
    kmeans = KMeans(n_clusters=N_CLUSTERS, n_init=25, random_state=42)
    labels = kmeans.fit_predict(Xz)

    agg["PC1"] = Z[:,0]
    agg["PC2"] = Z[:,1]
    agg["cluster"] = labels

    # --- Guardar CSV ---
    out_file = os.path.join(DATA_DIR, f"{TEAM.replace(' ', '_')}_{label_suffix}_defense_clusters.csv")
    agg.to_csv(out_file, index=False)
    print(f"✅ Archivo guardado en: {out_file}")

    # --- Radar charts ---
    cluster_means = agg.groupby("cluster")[features].mean().reset_index()
    cluster_norm = cluster_means.copy()
    for c in features:
        max_val = agg[c].max()
        min_val = agg[c].min()
        cluster_norm[c] = (cluster_means[c] - min_val) / (max_val - min_val)

    colors = plt.cm.tab10.colors
    for i in range(len(cluster_norm)):
        values = cluster_norm.loc[i, features]
        radar_path = os.path.join(DATA_DIR, f"{TEAM.replace(' ', '_')}_{label_suffix}_Cluster{i}_radar.png")
        make_radar(values, features, f"{label_suffix} - Cluster {i}", colors[i % 10], radar_path)

# ==========================================
# MAIN
# ==========================================
def main():
    load_dotenv(dotenv_path="../.env")
    EMAIL = os.getenv("STATSBOMB_USER")
    PASSWORD = os.getenv("STATSBOMB_PASS")
    CREDS = {"user": EMAIL, "passwd": PASSWORD}

    events_csv  = os.path.join(DATA_DIR, f"{TEAM.replace(' ', '_')}_events.csv")
    if not os.path.exists(events_csv):
        raise FileNotFoundError("No se encontró el archivo de eventos. Ejecuta primero build_defense_clusters.py")

    events_df = pd.read_csv(events_csv, low_memory=False)
    for c in ["type","duel","pass","location"]:
        if c in events_df.columns and events_df[c].dtype == object:
            events_df[c] = events_df[c].apply(lambda x: ast.literal_eval(x) if isinstance(x,str) and (x.startswith("{") or x.startswith("[")) else x)

    df = events_df[events_df["player_id"].notna()].copy()

    defenders = {
        "CB": ["Centre Back"],
        "FB": ["Left Back", "Right Back"]
    }

    for label, positions in defenders.items():
        process_defenders(df, positions, label)

# ==========================================
# EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    main()