import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "data"

# ─── Configuration par pays ────────────────────────────────────────────────────
COUNTRY_CONFIG = {
    "allemagne": {
        "data_dir": BASE_DIR / "data_allemagne",
        "files": {
            "gen":     "Actual_generation_hour.csv",
            "cons":    "Actual_consumption_Hour.csv",
            "price":   "Day-ahead_prices_hour.csv",
            "fcons":   "Forecasted_consumption_hour.csv",
            "fgen":    "Forecasted_generation_Day-Ahead_Hour.csv",
            "crossb":  "Cross-border_physical_flows_hour.csv",
            "instgen": "Installed_generation_capacity_hour.csv",
            "tso":     "Costs_of_TSOs__without_costs_of_DSOs_hour.csv",
            #"weather": "Weather_hourly_germany_2024_2025.csv",
        },
        "gen_map": {
            "Nuclear [MWh] Calculated resolutions":              "nuclear",
            "Biomass [MWh] Calculated resolutions":              "biomass",
            "Lignite [MWh] Calculated resolutions":              "lignite",
            "Hard coal [MWh] Calculated resolutions":            "coal",
            "Fossil gas [MWh] Calculated resolutions":           "gas",
            "Hydro pumped storage [MWh] Calculated resolutions": "hydro_pumped",
            "Hydropower [MWh] Calculated resolutions":           "hydro",
            "Wind offshore [MWh] Calculated resolutions":        "wind_off",
            "Wind onshore [MWh] Calculated resolutions":         "wind_on",
            "Photovoltaics [MWh] Calculated resolutions":        "solar",
            "Other renewable [MWh] Calculated resolutions":      "other_res",
            "Other conventional [MWh] Calculated resolutions":   "other_conv",
        },
        "cons_map": {
            "grid load [MWh] Calculated resolutions":                            "load",
            "Grid load incl. hydro pumped storage [MWh] Calculated resolutions": "load_incl_pumped",
            "Hydro pumped storage [MWh] Calculated resolutions":                 "pumped_consumption",
            "Residual load [MWh] Calculated resolutions":                        "residual_load_tso",
        },
        "price_map": {
            "Germany/Luxembourg [€/MWh] Calculated resolutions": "price",
            "∅ DE/LU neighbours [€/MWh] Calculated resolutions": "price_de_lu",
            "France [€/MWh] Calculated resolutions":             "price_fr",
            "Netherlands [€/MWh] Calculated resolutions":        "price_nl",
            "Austria [€/MWh] Calculated resolutions":            "price_at",
            "Poland [€/MWh] Calculated resolutions":             "price_pl",
            "Denmark 1 [€/MWh] Calculated resolutions":          "price_dk1",
            "Switzerland [€/MWh] Calculated resolutions":        "price_ch",
        },
        "fcons_map": {
            "grid load [MWh] Calculated resolutions":     "load_forecast",
            "Residual load [MWh] Calculated resolutions": "residual_load_forecast_tso",
        },
        "fgen_map": {
            "Wind offshore [MWh] Calculated resolutions":          "wind_off_forecast",
            "Wind onshore [MWh] Calculated resolutions":           "wind_on_forecast",
            "Photovoltaics [MWh] Calculated resolutions":          "solar_forecast",
            "Photovoltaics and wind [MWh] Calculated resolutions": "vre_forecast_total",
            "Total [MWh] Calculated resolutions":                  "total_generation_forecast",
        },
        "crossb_map": {
            "Net export [MWh] Calculated resolutions": "net_export_total",
        },
        "instgen_map": {
            "Nuclear [MW] Calculated resolutions":              "cap_nuclear",
            "Biomass [MW] Calculated resolutions":              "cap_biomass",
            "Lignite [MW] Calculated resolutions":              "cap_lignite",
            "Hard coal [MW] Calculated resolutions":            "cap_coal",
            "Fossil gas [MW] Calculated resolutions":           "cap_gas",
            "Hydro pumped storage [MW] Calculated resolutions": "cap_hydro_pumped",
            "Hydropower [MW] Calculated resolutions":           "cap_hydro",
            "Wind offshore [MW] Calculated resolutions":        "cap_wind_off",
            "Wind onshore [MW] Calculated resolutions":         "cap_wind_on",
            "Photovoltaics [MW] Calculated resolutions":        "cap_solar",
            "Other renewable [MW] Calculated resolutions":      "cap_other_res",
            "Other conventional [MW] Calculated resolutions":   "cap_other_conv",
        },
    },

    "france": {
        "data_dir": BASE_DIR / "data_france",
        "files": {
            "gen":     "Actual_generation_hour.csv",
            "cons":    "Actual_consumption_Hour.csv",
            "price":   "Day-ahead_prices_hour.csv",
            "price_de":"Day-ahead_prices_hour_de.csv",
            "fcons":   "Forecasted_consumption_hour.csv",
            "fgen":    "Forecasted_generation_Day-Ahead_Hour.csv",
            "crossb":  "Cross-border_physical_flows_hour.csv",
            "instgen": "Installed_generation_capacity_hour.csv",
            #"weather": "Weather_hourly_france_2024_2025.csv",
            # pas de TSO pour la France
        },
        "gen_map": {
            "Nuclear [MWh] Calculated resolutions":                  "nuclear",
            "Biomass [MWh] Calculated resolutions":                  "biomass",
            "Fossil gas [MWh] Calculated resolutions":               "gas",
            "Fossil hard coal [MWh] Calculated resolutions":         "coal",
            "Fossil oil [MWh] Calculated resolutions":               "oil",
            "Hydro pumped storage [MWh] Calculated resolutions":     "hydro_pumped",
            "Hydro Run-of-River [MWh] Calculated resolutions":       "hydro_ror",
            "Hydro water reservoir [MWh] Calculated resolutions":    "hydro_res",
            "Wind offshore [MWh] Calculated resolutions":            "wind_off",
            "Wind onshore [MWh] Calculated resolutions":             "wind_on",
            "Solar [MWh] Calculated resolutions":                    "solar",
            "Waste [MWh] Calculated resolutions":                    "waste",
        },
        "cons_map": {
            "Load [MWh] Calculated resolutions":                             "load",
            "Residual load [MWh] Calculated resolutions":                    "residual_load_tso",
            "Hydro pumped storage consumption [MWh] Calculated resolutions": "pumped_consumption",
        },
        "price_map": {
            "France [€/MWh] Calculated resolutions":             "price",
            "Germany/Luxembourg [€/MWh] Calculated resolutions": "price_de_lu",
            "Spain [€/MWh] Calculated resolutions":              "price_es",
            "Italy North [€/MWh] Calculated resolutions":        "price_it",
            "Belgium [€/MWh] Calculated resolutions":            "price_be",
            "Switzerland [€/MWh] Calculated resolutions":        "price_ch",
            "Netherlands [€/MWh] Calculated resolutions":        "price_nl",
            "Austria [€/MWh] Calculated resolutions":            "price_at",
            "Poland [€/MWh] Calculated resolutions":             "price_pl",
            "Denmark 1 [€/MWh] Calculated resolutions":          "price_dk1",
            "Portugal [€/MWh] Calculated resolutions":           "price_pt",
        },
        "price_de_map": {
            # Source : SMARD Allemagne — données complémentaires
            "∅ DE/LU neighbours [€/MWh] Calculated resolutions": "price_de_avg",
            "Germany/Luxembourg [€/MWh] Calculated resolutions": "price_de_smard",
        },
        "fcons_map": {
            "Forecasted load J [MWh] Calculated resolutions":   "load_forecast",
            "Forecasted load J-1 [MWh] Calculated resolutions": "load_forecast_j1",
        },
        "fgen_map": {
            "Wind offshore [MWh] Calculated resolutions":          "wind_off_forecast",
            "Wind onshore [MWh] Calculated resolutions":           "wind_on_forecast",
            "Photovoltaics [MWh] Calculated resolutions":          "solar_forecast",
            "Photovoltaics and wind [MWh] Calculated resolutions": "vre_forecast_total",
        },
        "crossb_map": {
            "sum (net export) [MWh] Calculated resolutions": "net_export_total",
        },
        "instgen_map": {
            "Nuclear [MW] Calculated resolutions":                   "cap_nuclear",
            "Biomass [MW] Calculated resolutions":                   "cap_biomass",
            "Fossil gas [MW] Calculated resolutions":                "cap_gas",
            "Fossil hard coal [MW] Calculated resolutions":          "cap_coal",
            "Hydro pumped storage [MW] Calculated resolutions":      "cap_hydro_pumped",
            "Hydro Run-of-River [MW] Calculated resolutions":        "cap_hydro_ror",
            "Hydro water reservoir [MW] Calculated resolutions":     "cap_hydro_res",
            "Wind offshore [MW] Calculated resolutions":             "cap_wind_off",
            "Wind onshore [MW] Calculated resolutions":              "cap_wind_on",
            "Solar AC [MW] Calculated resolutions":                  "cap_solar",
        },
    },
}


# ─── Helpers bas niveau ────────────────────────────────────────────────────────
def read_smard_csv(path: Path) -> pd.DataFrame:
    """Lit un CSV au format SMARD/energy-charts et parse les colonnes de dates."""
    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8-sig",
        na_values=["-", ""],
        thousands=",",
        low_memory=False,
    )
    fmt = "%b %d, %Y %I:%M %p"
    df["Start date"] = pd.to_datetime(df["Start date"], format=fmt, errors="coerce")
    df["End date"]   = pd.to_datetime(df["End date"],   format=fmt, errors="coerce")
    return df


def pick_col(df: pd.DataFrame, contains: str) -> str:
    """Retourne le premier nom de colonne contenant une sous-chaîne (insensible à la casse)."""
    cols = [c for c in df.columns if contains.lower() in c.lower()]
    if not cols:
        raise ValueError(f"Aucune colonne ne contient : {contains}")
    return cols[0]



# ─── Chargement complet ────────────────────────────────────────────────────────
def load_data(country: str) -> pd.DataFrame:
    """
    Charge et prétraite toutes les données pour un pays.

    Parameters
    ----------
    country : "france" ou "allemagne"

    Returns
    -------
    pd.DataFrame indexé par timestamp (heure Paris / Berlin)
    """
    if country not in COUNTRY_CONFIG:
        raise ValueError(f"Pays inconnu : {country!r}. Choisir parmi : {list(COUNTRY_CONFIG)}")

    cfg      = COUNTRY_CONFIG[country]
    data_dir = cfg["data_dir"]
    files    = cfg["files"]

    def read(key):
        if key not in files:
            return None
        path = data_dir / files[key]
        if not path.exists():
            print(f"  [WARN] Fichier absent : {path.name}")
            return None
        return read_smard_csv(path)

    return preprocess_full(
        cons_df    = read("cons"),
        gen_df     = read("gen"),
        price_df   = read("price"),
        price_de_df = read("price_de"),
        fcons_df   = read("fcons"),
        fgen_df    = read("fgen"),
        crossb_df  = read("crossb"),
        instgen_df = read("instgen"),
        country    = country,
    )


# ─── Prétraitement ────────────────────────────────────────────────────────────

def preprocess_full(
    cons_df:    pd.DataFrame,
    gen_df:     pd.DataFrame,
    price_df:   pd.DataFrame,
    price_de_df: pd.DataFrame | None = None,
    fcons_df:   pd.DataFrame | None = None,
    fgen_df:    pd.DataFrame | None = None,
    crossb_df:  pd.DataFrame | None = None,
    instgen_df: pd.DataFrame | None = None,
    country:    str = "allemagne",
) -> pd.DataFrame:
    """
    Fusionne les tables (y compris la météo) et renomme les colonnes en noms standardisés.

    Parameters
    ----------
    country : "france" ou "allemagne" — détermine les mappings de colonnes et le fichier météo
    """
    cfg = COUNTRY_CONFIG[country]

    def prepare(df: pd.DataFrame | None) -> pd.DataFrame | None:
        if df is None:
            return None
        d = df.copy()
        d.columns = [c.replace('\ufeff', '') for c in d.columns]
        if "Start date" in d.columns:
            d["Start date"] = pd.to_datetime(d["Start date"], errors="coerce")
            d = d.set_index("Start date")
        d = d.drop(columns=["End date"], errors="ignore")
        d = d.sort_index()
        
        # Gestion des doublons sur l'index temporel
        if d.index.duplicated().any():
            d = d.groupby(level=0).mean(numeric_only=True)
        return d

    # --- Sous-fonction pour gérer la météo automatiquement ---
    def load_and_prepare_weather(country_name: str) -> pd.DataFrame | None:
        if country_name not in WEATHER_FILES:
            print(f"Info : Pas de fichier météo configuré pour {country_name}")
            return None
            
        path = Path(COUNTRY_CONFIG[country_name]["data_dir"]) / WEATHER_FILES[country_name]
        
        if not path.exists():
            print(f"Avertissement : Fichier météo introuvable pour {country_name} ({path})")
            return None

        WEATHER_VARS = [
            'windspeed_10m', 'windspeed_100m', 
            'shortwave_radiation', 'direct_radiation', 
            'temperature_2m', 'cloudcover'
        ]

        df_w = pd.read_csv(path, parse_dates=["time"])
        cols = ["time"] + [c for c in WEATHER_VARS if c in df_w.columns]
        
        return (
            df_w[cols]
            .groupby("time")
            .mean()
            .rename_axis("Start date")
        )

    # 1. Tables de base avec mapping
    df = prepare(price_df).rename(columns=cfg["price_map"])
    df = df.join(prepare(cons_df).rename(columns=cfg["cons_map"]),    how="left")
    df = df.join(prepare(gen_df).rename(columns=cfg["gen_map"]),      how="left")

    # 2. Tables optionnelles ENTSO-E avec mapping
    for opt_df, map_key in [
        (fcons_df,  "fcons_map"),
        (fgen_df,   "fgen_map"),
        (crossb_df, "crossb_map"),
        (instgen_df,"instgen_map"),
        (price_de_df, "price_de_map"),
    ]:
        if opt_df is not None:
            df = df.join(prepare(opt_df).rename(columns=cfg[map_key]), how="left")

    # 3. Ajout automatique de la Météo
    weather_df = load_and_prepare_weather(country)
    if weather_df is not None:
        # L'index est déjà "Start date" grâce à la sous-fonction
        df = df.join(weather_df, how="left")

    return df


# ─── Météo ────────────────────────────────────────────────────────────────────
WEATHER_FILES = {
    "france":    "Weather_hourly_france_2024_2025.csv",
    "allemagne": "Weather_hourly_germany_2024_2025.csv",
}

WEATHER_VARS = [
    "windspeed_10m", "windspeed_100m",
    "shortwave_radiation", "direct_radiation",
    "temperature_2m", "cloudcover",
]

#def load_weather(country: str) -> pd.DataFrame:
#    """
#    Charge la météo horaire et retourne la moyenne zonale par heure.
#    Index : timestamps naïfs en heure locale (même référence que load_data).
#    """
#    if country not in WEATHER_FILES:
#        raise ValueError(f"Météo non disponible pour : {country!r}")
#    path = COUNTRY_CONFIG[country]["data_dir"] / WEATHER_FILES[country]
#    if not path.exists():
#        raise FileNotFoundError(f"Fichier météo absent : {path}\nLance fetch_weather_germany() dans load_data.py")
#
#    df = pd.read_csv(path, parse_dates=["time"])
#    cols = ["time"] + [c for c in WEATHER_VARS if c in df.columns]
#    return (
#        df[cols]
#        .groupby("time")
#        .mean()
#        .rename_axis("Start date")
#    )


# ─── Feature engineering ──────────────────────────────────────────────────────
import pandas as pd
import numpy as np

def add_features(df: pd.DataFrame, drop_missing_critical: bool = True) -> pd.DataFrame:
    """Crée l'ensemble des features dérivées, dont l'estimation du curtailment (via marché et via météo)."""
    out = df.copy()

    # --- Temps ---
    out["hour"]       = out.index.hour
    out["weekday"]    = out.index.weekday
    out["is_weekend"] = (out["weekday"] >= 5).astype(int)
    out["hour_sin"]   = np.sin(2 * np.pi * out["hour"] / 24)
    out["hour_cos"]   = np.cos(2 * np.pi * out["hour"] / 24)

    # --- Génération agrégée ---
    out["wind_total"]     = out.get("wind_on", 0) + out.get("wind_off", 0)
    out["vre_real_total"] = out["wind_total"] + out.get("solar", 0)

    # Hydro : Allemagne = "hydro" / France = "hydro_ror" + "hydro_res"
    hydro_total = (
        out.get("hydro", 0)
        + out.get("hydro_ror", 0)
        + out.get("hydro_res", 0)
    )

    out["renewable_total"] = (
        out["vre_real_total"]
        + hydro_total
        + out.get("biomass", 0)
        + out.get("other_res", 0)
        + out.get("waste", 0)
    )

    out["thermal_total"] = (
        out.get("nuclear", 0)
        + out.get("lignite", 0)
        + out.get("coal", 0)
        + out.get("gas", 0)
        + out.get("oil", 0)
        + out.get("other_conv", 0)
    )

    # --- Demande & bilan ---
    if "load" in out.columns:
        out["residual_load"]           = out["load"] - out["vre_real_total"]
        out["total_generation"]        = out["renewable_total"] + out["thermal_total"]
        out["generation_load_balance"] = out["total_generation"] - out["load"]

    # --- Prévisions ---
    out["wind_forecast_total"] = (
        out.get("wind_off_forecast", 0) + out.get("wind_on_forecast", 0)
    )
    if "vre_forecast_total" not in out.columns:
        out["vre_forecast_total"] = (
            out["wind_forecast_total"] + out.get("solar_forecast", 0)
        )

    if "load_forecast" in out.columns:
        out["residual_load_forecast"] = out["load_forecast"] - out["vre_forecast_total"]
        denom = out["load_forecast"].replace(0, np.nan)
        out["vre_penetration_forecast"] = out["vre_forecast_total"] / denom

    # --- Curtailment (Basé sur les prévisions du marché) ---
    out["curtailment_raw_gap"] = (
        out["vre_forecast_total"] - out["vre_real_total"]
    ).clip(lower=0)

    # Capacity factors basés sur le réel
    cap_wind = out.get("cap_wind_on", 0) + out.get("cap_wind_off", 0)
    out["wind_capacity_factor"]  = out["wind_total"] / cap_wind.replace(0, np.nan)
    out["solar_capacity_factor"] = (
        out.get("solar", 0) / out.get("cap_solar", pd.Series(np.nan, index=out.index)).replace(0, np.nan)
    )

    if "price" in out.columns:
        out["is_negative"] = (out["price"] < 0).astype(int)

        price_threshold = 10
        out["is_curtailment_likely"] = (
            (out["curtailment_raw_gap"] > 50) &
            (out["price"] < price_threshold)
        ).astype(int)

        out["curtailment_mwh"] = out["curtailment_raw_gap"] * out["is_curtailment_likely"]

    # --- NOUVEAU : Curtailment (Basé sur la physique et la météo) ---
    if "windspeed_100m" in out.columns and "shortwave_radiation" in out.columns:
        
        # 1. Calcul du Facteur de Charge (CF) Éolien théorique
        v = out["windspeed_100m"].fillna(0)
        v_cut_in = 3.0
        v_rated = 12.0
        v_cut_out = 25.0
        
        out["wind_cf_weather"] = np.select(
            [
                v < v_cut_in,
                (v >= v_cut_in) & (v < v_rated),
                (v >= v_rated) & (v < v_cut_out),
                v >= v_cut_out
            ],
            [
                0.0,
                (v**3 - v_cut_in**3) / (v_rated**3 - v_cut_in**3), # Courbe cubique
                1.0,
                0.0
            ],
            default=0.0
        )
        
        # 2. Calcul du Facteur de Charge (CF) Solaire théorique (STC = 1000 W/m2)
        g = out["shortwave_radiation"].fillna(0)
        out["solar_cf_weather"] = (g / 1000.0).clip(upper=1.0)
        
        # Préparation sécurisée des capacités installées pour le calcul vectoriel
        cap_solar_s = out.get("cap_solar", pd.Series(0, index=out.index)).replace(np.nan, 0)
        cap_wind_s = cap_wind if isinstance(cap_wind, pd.Series) else pd.Series(cap_wind, index=out.index).replace(np.nan, 0)
        
        # 3. Calcul de la Production Théorique Météo (MWh)
        out["wind_theoretical_gen"] = out["wind_cf_weather"] * cap_wind_s
        out["solar_theoretical_gen"] = out["solar_cf_weather"] * cap_solar_s
        out["vre_theoretical_total"] = out["wind_theoretical_gen"] + out["solar_theoretical_gen"]
        
        # 4. Calcul de l'écrêtement physique (Théorie - Réalité)
        out["curtailment_physical_wind"] = (out["wind_theoretical_gen"] - out["wind_total"]).clip(lower=0)
        out["curtailment_physical_solar"] = (out["solar_theoretical_gen"] - out.get("solar", 0)).clip(lower=0)
        out["curtailment_physical_total"] = out["curtailment_physical_wind"] + out["curtailment_physical_solar"]
        
        # 5. Application du filtre économique sur l'écrêtement physique
        if "price" in out.columns:
            out["curtailment_physical_economic"] = np.where(
                out["price"] < price_threshold, 
                out["curtailment_physical_total"], 
                0
            )

    # --- Nettoyage ---
    if drop_missing_critical:
        critical = [c for c in ["price", "load_forecast", "vre_real_total"] if c in out.columns]
        if critical:
            out = out.dropna(subset=critical)

    return out
