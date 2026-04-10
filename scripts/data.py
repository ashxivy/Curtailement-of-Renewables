import pandas as pd
import numpy as np
from pathlib import Path



def read_smard_csv(path: Path) -> pd.DataFrame:
    """Read a SMARD CSV and parse Start/End date columns."""
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
    df["End date"] = pd.to_datetime(df["End date"], format=fmt, errors="coerce")
    return df


def pick_col(df: pd.DataFrame, contains: str) -> str:
    """Return first column name containing a substring (case-insensitive)."""
    cols = [c for c in df.columns if contains.lower() in c.lower()]
    if not cols:
        raise ValueError(f"Aucune colonne ne contient : {contains}")
    return cols[0]


import pandas as pd

def preprocess_full(
    cons_df: pd.DataFrame,
    gen_df: pd.DataFrame,
    price_df: pd.DataFrame,
    fcons_df: pd.DataFrame | None = None,
    fgen_df: pd.DataFrame | None = None,
    crossb_df: pd.DataFrame | None = None,
    instgen_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Prepare + merge SMARD tables including installed capacity.
    """
    def prepare(df: pd.DataFrame | None) -> pd.DataFrame | None:
        if df is None:
            return None
        d = df.copy()

        # Nettoyage des noms de colonnes pour gérer les caractères cachés (BOM UTF-8)
        # fréquent dans les exports SMARD (ex: '\ufeffStart date')
        d.columns = [c.replace('\ufeff', '') for c in d.columns]

        if "Start date" in d.columns:
            d["Start date"] = pd.to_datetime(d["Start date"], errors="coerce")
            d = d.set_index("Start date")

        d = d.drop(columns=["End date"], errors="ignore")
        d = d.sort_index()
        return d

    # --- Mappings ---
    gen_map = {
        "Nuclear [MWh] Calculated resolutions": "nuclear",
        "Biomass [MWh] Calculated resolutions": "biomass",
        "Lignite [MWh] Calculated resolutions": "lignite",
        "Hard coal [MWh] Calculated resolutions": "coal",
        "Fossil gas [MWh] Calculated resolutions": "gas",
        "Hydro pumped storage [MWh] Calculated resolutions": "hydro_pumped",
        "Hydropower [MWh] Calculated resolutions": "hydro",
        "Wind offshore [MWh] Calculated resolutions": "wind_off",
        "Wind onshore [MWh] Calculated resolutions": "wind_on",
        "Photovoltaics [MWh] Calculated resolutions": "solar",
        "Other renewable [MWh] Calculated resolutions": "other_res",
        "Other conventional [MWh] Calculated resolutions": "other_conv",
    }

    cons_map = {
        "grid load [MWh] Calculated resolutions": "load",
        "Grid load incl. hydro pumped storage [MWh] Calculated resolutions": "load_incl_pumped",
        "Hydro pumped storage [MWh] Calculated resolutions": "pumped_consumption",
        "Residual load [MWh] Calculated resolutions": "residual_load_tso",
    }

    price_map = {
        "Germany/Luxembourg [€/MWh] Calculated resolutions": "price",
        "∅ DE/LU neighbours [€/MWh] Calculated resolutions": "price_de_lu",
        "France [€/MWh] Calculated resolutions": "price_fr",
        "Netherlands [€/MWh] Calculated resolutions": "price_nl",
        "Austria [€/MWh] Calculated resolutions": "price_at",
        "Poland [€/MWh] Calculated resolutions": "price_pl",
        "Denmark 1 [€/MWh] Calculated resolutions": "price_dk1",
        "Switzerland [€/MWh] Calculated resolutions": "price_ch",
    }

    fcons_map = {
        "grid load [MWh] Calculated resolutions": "load_forecast",
        "Residual load [MWh] Calculated resolutions": "residual_load_forecast_tso",
    }

    fgen_map = {
        "Wind offshore [MWh] Calculated resolutions": "wind_off_forecast",
        "Wind onshore [MWh] Calculated resolutions": "wind_on_forecast",
        "Photovoltaics [MWh] Calculated resolutions": "solar_forecast",
        "Photovoltaics and wind [MWh] Calculated resolutions": "vre_forecast_total",
        "Total [MWh] Calculated resolutions": "total_generation_forecast",
    }

    crossb_map = {"Net export [MWh] Calculated resolutions": "net_export_total"}

    # Nouveau mapping pour la capacité installée
    instgen_map = {
        "Nuclear [MW] Calculated resolutions": "cap_nuclear",
        "Biomass [MW] Calculated resolutions": "cap_biomass",
        "Lignite [MW] Calculated resolutions": "cap_lignite",
        "Hard coal [MW] Calculated resolutions": "cap_coal",
        "Fossil gas [MW] Calculated resolutions": "cap_gas",
        "Hydro pumped storage [MW] Calculated resolutions": "cap_hydro_pumped",
        "Hydropower [MW] Calculated resolutions": "cap_hydro",
        "Wind offshore [MW] Calculated resolutions": "cap_wind_off",
        "Wind onshore [MW] Calculated resolutions": "cap_wind_on",
        "Photovoltaics [MW] Calculated resolutions": "cap_solar",
        "Other renewable [MW] Calculated resolutions": "cap_other_res",
        "Other conventional [MW] Calculated resolutions": "cap_other_conv",
    }

    # --- Merging ---
    df = prepare(price_df).rename(columns=price_map)
    df = df.join(prepare(cons_df).rename(columns=cons_map), how="left")
    df = df.join(prepare(gen_df).rename(columns=gen_map), how="left")

    optional = [
        (fcons_df, fcons_map),
        (fgen_df, fgen_map),
        (crossb_df, crossb_map),
        (instgen_df, instgen_map), # Ajout de la nouvelle table ici
    ]

    for opt_df, mapping in optional:
        if opt_df is not None:
            df = df.join(prepare(opt_df).rename(columns=mapping), how="left")

    return df


import numpy as np
import pandas as pd

def add_features(df: pd.DataFrame, drop_missing_critical: bool = True) -> pd.DataFrame:
    """Create a complete set of engineered features, including curtailment estimation."""
    out = df.copy()

    # --- Time features ---
    out["hour"] = out.index.hour
    out["weekday"] = out.index.weekday
    out["is_weekend"] = (out["weekday"] >= 5).astype(int)
    out["hour_sin"] = np.sin(2 * np.pi * out["hour"] / 24)
    out["hour_cos"] = np.cos(2 * np.pi * out["hour"] / 24)

    # --- Aggregated Real Generation ---
    out["wind_total"] = out.get("wind_on", 0) + out.get("wind_off", 0)
    out["vre_real_total"] = out["wind_total"] + out.get("solar", 0)
    
    out["renewable_total"] = (
        out["vre_real_total"]
        + out.get("hydro", 0)
        + out.get("biomass", 0)
        + out.get("other_res", 0)
    )

    out["thermal_total"] = (
        out.get("nuclear", 0)
        + out.get("lignite", 0)
        + out.get("coal", 0)
        + out.get("gas", 0)
        + out.get("other_conv", 0)
    )

    # --- Demand & Balance ---
    if "load" in out.columns:
        out["residual_load"] = out["load"] - out["vre_real_total"]
        out["total_generation"] = out["renewable_total"] + out["thermal_total"]
        out["generation_load_balance"] = out["total_generation"] - out["load"]

    # --- Forecasts ---
    out["wind_forecast_total"] = out.get("wind_off_forecast", 0) + out.get("wind_on_forecast", 0)
    if "vre_forecast_total" not in out.columns:
        out["vre_forecast_total"] = out["wind_forecast_total"] + out.get("solar_forecast", 0)

    if "load_forecast" in out.columns:
        out["residual_load_forecast"] = out["load_forecast"] - out["vre_forecast_total"]
        denom = out["load_forecast"].replace(0, np.nan)
        out["vre_penetration_forecast"] = out["vre_forecast_total"] / denom

    # --- CURTAILMENT FEATURES ---
    
    # 1. Raw Gap (Potentiel - Réel)
    # Si > 0, on a produit moins que le potentiel prévu.
    out["curtailment_raw_gap"] = (out["vre_forecast_total"] - out["vre_real_total"]).clip(lower=0)

    # 2. Capacity Factors (Usage réel vs Capacité installée)
    # Wind
    cap_wind = out.get("cap_wind_on", 0) + out.get("cap_wind_off", 0)
    out["wind_capacity_factor"] = out["wind_total"] / cap_wind.replace(0, np.nan)
    
    # Solar
    out["solar_capacity_factor"] = out.get("solar", 0) / out.get("cap_solar", np.nan).replace(0, np.nan)

    # 3. Refined Curtailment Estimation
    # On considère que c'est du curtailment si : gap > 0 ET prix très bas (seuil < 10€)
    if "price" in out.columns:
        out["is_negative"] = (out["price"] < 0).astype(int)
        
        # Seuil de prix pour identifier le curtailment économique
        price_threshold = 10 
        out["is_curtailment_likely"] = (
            (out["curtailment_raw_gap"] > 50) & # Filtre le bruit (ex: > 50 MW)
            (out["price"] < price_threshold)
        ).astype(int)

        # La valeur de l'énergie perdue
        out["curtailment_mwh"] = out["curtailment_raw_gap"] * out["is_curtailment_likely"]

    # --- Cleaning ---
    if drop_missing_critical:
        critical = [c for c in ["price", "load_forecast", "vre_real_total"] if c in out.columns]
        if critical:
            out = out.dropna(subset=critical)

    return out