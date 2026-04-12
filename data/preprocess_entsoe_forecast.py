"""
Prétraitement des fichiers ENTSO-E "Generation Forecast for Wind & Solar" — France
============================================================================
Entrées : 6 fichiers CSV ENTSO-E déposés dans data/
    GUI_WIND_SOLAR_GENERATION_FORECAST_SOLAR_202312312300-202412312300.csv
    GUI_WIND_SOLAR_GENERATION_FORECAST_SOLAR_202412312300-202512312300.csv
    GUI_WIND_SOLAR_GENERATION_FORECAST_ONSHORE_202312312300-202412312300.csv
    GUI_WIND_SOLAR_GENERATION_FORECAST_ONSHORE_202412312300-202512312300.csv
    GUI_WIND_SOLAR_GENERATION_FORECAST_OFFSHORE_202312312300-202412312300.csv
    GUI_WIND_SOLAR_GENERATION_FORECAST_OFFSHORE_202412312300-202512312300.csv

Sortie : data_france/Forecasted_generation_Day-Ahead_Hour.csv
         Format identique à data_allemagne/Forecasted_generation_Day-Ahead_Hour.csv
============================================================================
"""

import pandas as pd
from pathlib import Path
from datetime import timedelta

DATA_DIR   = Path(__file__).parent
OUTPUT_DIR = DATA_DIR / "data_france"
ENTSOE_DIR = OUTPUT_DIR  # les fichiers ENTSO-E sont dans data_france/

FILES = {
    "solar": [
        ENTSOE_DIR / "GUI_WIND_SOLAR_GENERATION_FORECAST_SOLAR_202312312300-202412312300.csv",
        ENTSOE_DIR / "GUI_WIND_SOLAR_GENERATION_FORECAST_SOLAR_202412312300-202512312300.csv",
    ],
    "onshore": [
        ENTSOE_DIR / "GUI_WIND_SOLAR_GENERATION_FORECAST_ONSHORE_202312312300-202412312300.csv",
        ENTSOE_DIR / "GUI_WIND_SOLAR_GENERATION_FORECAST_ONSHORE_202412312300-202512312300.csv",
    ],
    "offshore": [
        ENTSOE_DIR / "GUI_WIND_SOLAR_GENERATION_FORECAST_OFFSHORE_202312312300-202412312300.csv",
        ENTSOE_DIR / "GUI_WIND_SOLAR_GENERATION_FORECAST_OFFSHORE_202412312300-202512312300.csv",
    ],
}


def fmt_dt(dt):
    months = ['Jan','Feb','Mar','Apr','May','Jun',
              'Jul','Aug','Sep','Oct','Nov','Dec']
    h    = dt.hour % 12 or 12
    ampm = 'AM' if dt.hour < 12 else 'PM'
    return f"{months[dt.month-1]} {dt.day}, {dt.year} {h}:{dt.minute:02d} {ampm}"


def load_series(files, col):
    """Charge et concatène les fichiers ENTSO-E, extrait la colonne Day-ahead (MW)."""
    dfs = []
    for f in files:
        df = pd.read_csv(f, quotechar='"')
        df = df.rename(columns={"MTU (CET/CEST)": "mtu", "Day-ahead (MW)": col})
        df = df[["mtu", col]].copy()
        # Parse le timestamp de début : "01/01/2024 00:00:00 (CET) - 01/01/2024 01:00:00 (CET)"
        start_str = (
            df["mtu"].str.split(" - ").str[0]
            .str.replace(r"\s*\([^)]+\)", "", regex=True)  # supprime (CET) et (CEST)
            .str.strip()
        )
        df["dt"] = pd.to_datetime(
            start_str,
            format="%d/%m/%Y %H:%M:%S"
        ).dt.tz_localize(
            "Europe/Paris",
            ambiguous="infer",        # gère l'heure d'été → heure d'hiver (doublon)
            nonexistent="shift_forward"  # gère le passage heure d'hiver → heure d'été
        )
        dfs.append(df[["dt", col]])
    combined = (
        pd.concat(dfs)
        .drop_duplicates("dt")
        .sort_values("dt")
        .set_index("dt")
    )
    return combined


# ─── Chargement des 3 séries ──────────────────────────────────────────────────
print("Chargement des fichiers ENTSO-E...")
solar    = load_series(FILES["solar"],    "Photovoltaics [MWh] Calculated resolutions")
onshore  = load_series(FILES["onshore"],  "Wind onshore [MWh] Calculated resolutions")
offshore = load_series(FILES["offshore"], "Wind offshore [MWh] Calculated resolutions")

df = solar.join(onshore, how="outer").join(offshore, how="outer")

# Filtrer strictement 2024-2025
df = df[
    (df.index >= pd.Timestamp("2024-01-01", tz="Europe/Paris")) &
    (df.index <  pd.Timestamp("2026-01-01", tz="Europe/Paris"))
].copy()

print(f"  Période : {df.index[0]}  →  {df.index[-1]}")
print(f"  Lignes  : {len(df):,}")

# Colonne agrégée : Photovoltaics and wind = somme des 3
df["Photovoltaics and wind [MWh] Calculated resolutions"] = (
    df["Wind onshore [MWh] Calculated resolutions"].fillna(0) +
    df["Wind offshore [MWh] Calculated resolutions"].fillna(0) +
    df["Photovoltaics [MWh] Calculated resolutions"].fillna(0)
)

# ─── Formatage au format data_allemagne ───────────────────────────────────────
rows = []
for dt, row in df.iterrows():
    dt_py = dt.to_pydatetime()
    rows.append({
        "Start date":  fmt_dt(dt_py),
        "End date":    fmt_dt(dt_py + timedelta(hours=1)),
        "Photovoltaics and wind [MWh] Calculated resolutions":
            row["Photovoltaics and wind [MWh] Calculated resolutions"],
        "Wind offshore [MWh] Calculated resolutions":
            row["Wind offshore [MWh] Calculated resolutions"],
        "Wind onshore [MWh] Calculated resolutions":
            row["Wind onshore [MWh] Calculated resolutions"],
        "Photovoltaics [MWh] Calculated resolutions":
            row["Photovoltaics [MWh] Calculated resolutions"],
    })

out = pd.DataFrame(rows)
out_path = OUTPUT_DIR / "Forecasted_generation_Day-Ahead_Hour.csv"
out.to_csv(out_path, index=False, sep=";")

print(f"\n✅  {out_path}  ({len(out):,} lignes)")
print(f"    {rows[0]['Start date']}  →  {rows[-1]['Start date']}")

# ─── Vérification rapide ──────────────────────────────────────────────────────
print("\nAperçu (premières lignes) :")
print(out.head(3).to_string(index=False))
print("\nValeurs manquantes par colonne :")
print(out.isnull().sum())
