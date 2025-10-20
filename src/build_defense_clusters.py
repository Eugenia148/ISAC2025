# ==========================================
# build_defense_clusters.py
# ISAC 2025 – Club América | Liga MX
# Generates defensive metrics and groups player profiles
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

np.random.seed(42)

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================
DATA_DIR   = "../data"
TEAM       = "América"
COMP_ID    = 108
SEASON_ID  = 506
N_CLUSTERS = 5

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def safe_len(x):
    try: return len(x)
    except: return 0

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


# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================
def main():
    # --- Cargar credenciales ---
    load_dotenv(dotenv_path="../.env")
    EMAIL = os.getenv("STATSBOMB_USER")
    PASSWORD = os.getenv("STATSBOMB_PASS")
    if not EMAIL or not PASSWORD:
        raise ValueError("Credenciales StatsBomb no encontradas en .env")

    CREDS = {"user": EMAIL, "passwd": PASSWORD}
    os.makedirs(DATA_DIR, exist_ok=True)

    matches_csv = os.path.join(DATA_DIR, f"{TEAM.replace(' ', '_')}_matches.csv")
    events_csv  = os.path.join(DATA_DIR, f"{TEAM.replace(' ', '_')}_events.csv")

    # --- Cargar o descargar datos ---
    if os.path.exists(matches_csv) and os.path.exists(events_csv):
        print("Cargando datos locales…")
        matches = pd.read_csv(matches_csv)
        events_df = pd.read_csv(events_csv, low_memory=False)
    else:
        print("Descargando datos desde la API (Liga MX)…")
        try:
            matches = sb.matches(competition_id=COMP_ID, season_id=SEASON_ID, creds=CREDS)
        except Exception as e:
            print("Error con IDs fijos, buscando competencia Liga MX:", e)
            comps = sb.competitions(creds=CREDS)
            mx_comp = comps[comps["competition_name"].str.contains("Liga MX", case=False)]
            mx_comp = mx_comp.sort_values("season_id", ascending=False).head(1)
            comp_id = int(mx_comp.iloc[0]["competition_id"])
            season_id = int(mx_comp.iloc[0]["season_id"])
            matches = sb.matches(competition_id=comp_id, season_id=season_id, creds=CREDS)

        team_matches = matches[(matches['home_team'] == TEAM) | (matches['away_team'] == TEAM)]
        team_matches.to_csv(matches_csv, index=False)
        print(f" {len(team_matches)} partidos encontrados de {TEAM}.")

        all_events = []
        for mid in team_matches['match_id']:
            print(f" Descargando eventos del partido {mid}…")
            ev = sb.events(match_id=mid, creds=CREDS)
            ev["match_id"] = mid
            all_events.append(ev)

        events_df = pd.concat(all_events, ignore_index=True)
        events_df.to_csv(events_csv, index=False)
        print("Eventos guardados correctamente.")

    # --- Reconstrucción JSON ---
    for c in ["type","duel","pass","location"]:
        if c in events_df.columns and events_df[c].dtype == object:
            events_df[c] = events_df[c].apply(lambda x: ast.literal_eval(x) if isinstance(x,str) and (x.startswith("{") or x.startswith("[")) else x)

    # --- Crear variables defensivas ---
    df = events_df[events_df["player_id"].notna()].copy()
    df["start_x"] = df.apply(get_start_x, axis=1)
    df["end_x"]   = df.apply(get_end_x, axis=1)
    df["pass_len"] = df.apply(pass_length, axis=1)
    df["pass_completed"] = df.apply(is_completed_pass, axis=1)

    df["is_tackle"]       = df.apply(lambda x: is_event(x,"Tackle"), axis=1)
    df["is_interception"] = df.apply(lambda x: is_event(x,"Interception"), axis=1)
    df["is_clearance"]    = df.apply(lambda x: is_event(x,"Clearance"), axis=1)
    df["is_pressure"]     = df.apply(lambda x: is_event(x,"Pressure"), axis=1)
    df["is_recovery"]     = df.apply(lambda x: is_event(x,"Ball Recovery"), axis=1)
    df["is_dribbled_past"]= df.apply(lambda x: is_event(x,"Dribbled Past"), axis=1)

    # Funciones seguras para duelos aéreos
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

    # Aplicar funciones
    df["is_aerial"]  = df.apply(is_aerial_duel, axis=1)
    df["aerial_won"] = df.apply(is_aerial_won, axis=1)

    # Variables espaciales y de pase
    df["fhalf_pressure"]  = df["is_pressure"] & (df["start_x"]>60)
    df["forward_pass"]    = (df["pass_len"].notna()) & (df["end_x"]>df["start_x"])
    df["long_ball"]       = df["pass_len"]>30
    df["long_ball_completed"] = df["long_ball"] & df["pass_completed"]

    # --- Filtrar por tipo de defensor ---
    # Mostrar las posiciones disponibles
    print("Posiciones únicas en los eventos:", df["position"].dropna().unique())

    # Elegir filtro:
    # 1️⃣ Solo defensas centrales (CB)
    # df = df[df["position"].isin(["Centre Back"])]

    # 2️⃣ Solo laterales (LB/RB)
    # df = df[df["position"].isin(["Left Back", "Right Back"])]

    # 3️⃣ Todos los defensores (centrales + laterales)
    # df = df[df["position"].isin(["Centre Back", "Left Back", "Right Back"])]

    print(f" Jugadores defensivos seleccionados: {df['player'].nunique()}")

    # --- Asegurar columna 'player_name' ---
    if "player_name" not in df.columns:
        if "player" in df.columns:
            df = df.rename(columns={"player": "player_name"})
        elif "player.name" in df.columns:
            df = df.rename(columns={"player.name": "player_name"})
        else:
            raise KeyError("No se encontró ninguna columna de nombre del jugador (player_name o player).")

    # --- Agregación por jugador ---
    
    agg = df.groupby(["player_id","player_name"]).agg(
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
            df.loc[s.index, "start_x"][
                df.loc[s.index,"is_tackle"] | df.loc[s.index,"is_interception"]
            ]
        )),
        avg_x_pressure=("start_x", lambda s: np.nanmean(
            df.loc[s.index,"start_x"][df.loc[s.index,"is_pressure"]]
        ))
    ).reset_index()

    # --- Minutos (temporal: asumimos 900) ---
    agg["minutes"] = 900

    # --- Métricas por 90 y ratios ---
    m = agg["minutes"].replace({0:np.nan})
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

    # --- Guardar resultados ---
    out_path = os.path.join(DATA_DIR, f"{TEAM.replace(' ', '_')}_defense_clusters.csv")
    agg.to_csv(out_path, index=False)
    centroids = pd.DataFrame(kmeans.cluster_centers_, columns=features)
    centroids.to_csv(os.path.join(DATA_DIR, f"{TEAM.replace(' ', '_')}_centroids.csv"), index=False)

    print(f" Archivo guardado en: {out_path}")
    print("\n Promedios por cluster:")
    print(agg.groupby("cluster")[features].mean().round(2))

    # --- Visualización ---
    plt.figure(figsize=(8,6))
    colors = plt.cm.tab10.colors
    for c in sorted(agg["cluster"].unique()):
        sub = agg[agg["cluster"]==c]
        plt.scatter(sub["PC1"], sub["PC2"], s=90, color=colors[c%10], label=f"Cluster {c}", alpha=0.8)
    for _, r in agg.iterrows():
        plt.text(r["PC1"]+0.02, r["PC2"], r["player_name"], fontsize=8)
    plt.title(f"Clústeres defensivos - {TEAM} (Liga MX 23/24)")
    plt.legend()
    plt.show()

# ==========================================
# EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    main()
