"""
====================================================================
Données énergétiques France — équivalent data_allemagne
====================================================================
Produit 8 CSV au format identique aux fichiers Allemagne + 1 météo :

  1. Actual_generation_hour.csv         → energy-charts.info (public_power)
  2. Actual_consumption_Hour.csv        → energy-charts.info (public_power)
  3. Day-ahead_prices_hour.csv          → energy-charts.info (price)
  4. Installed_generation_capacity_hour.csv → energy-charts.info (installed_power)
  5. Cross-border_physical_flows_hour.csv   → energy-charts.info (cbet)
  6. Forecasted_consumption_hour.csv    → ODRÉ éCO2mix (prevision_j/j1)
  7. Forecasted_generation_Day-Ahead_Hour.csv → energy-charts.info (ren_share_forecast)
  8. Costs_of_TSOs__without_costs_of_DSOs_hour.csv → placeholder (non publié pour FR)
  9. Weather_hourly_france.csv          → Open-Meteo

Sources gratuites, sans inscription.
====================================================================
"""

import os
import calendar
import time
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# ─── Configuration ────────────────────────────────────────────────────────────
COUNTRY    = "fr"
BZN        = "FR"
START_YEAR = 2024
END_YEAR   = 2025
OUTPUT_DIR = "data_france"

BASE_EC  = "https://api.energy-charts.info"
BASE_ODRE = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets"
HEADERS  = {"User-Agent": "Mozilla/5.0"}
TZ       = ZoneInfo("Europe/Paris")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def ts_to_paris(unix_seconds):
    return [datetime.fromtimestamp(ts, tz=TZ) for ts in unix_seconds]

def fmt_dt(dt):
    """Format identique aux fichiers Allemagne : 'Jan 1, 2024 12:00 AM'"""
    months = ['Jan','Feb','Mar','Apr','May','Jun',
              'Jul','Aug','Sep','Oct','Nov','Dec']
    h = dt.hour % 12 or 12
    ampm = 'AM' if dt.hour < 12 else 'PM'
    return f"{months[dt.month-1]} {dt.day}, {dt.year} {h}:{dt.minute:02d} {ampm}"

def build_rows(unix_seconds, series, freq_h=1):
    dts = ts_to_paris(unix_seconds)
    rows = []
    for i, dt in enumerate(dts):
        row = {"Start date": fmt_dt(dt), "End date": fmt_dt(dt + timedelta(hours=freq_h))}
        for col, vals in series.items():
            row[col] = vals[i] if i < len(vals) else None
        rows.append(row)
    return rows

def save_csv(rows, filename):
    path = f"{OUTPUT_DIR}/{filename}"
    pd.DataFrame(rows).to_csv(path, index=False, sep=';')
    print(f"  ✅ {filename}  ({len(rows):,} lignes)")

def ec_get(endpoint, params=""):
    url = f"{BASE_EC}/{endpoint}?country={COUNTRY}{params}"
    r = requests.get(url, timeout=60, headers=HEADERS)
    r.raise_for_status()
    return r.json()


# ─── 1+2. Génération actuelle + Consommation (public_power) ──────────────────
def fetch_public_power():
    print("\n[1+2/8] Génération + consommation actuelles (energy-charts.info)...")

    GEN_COLS   = ["Wind onshore", "Wind offshore", "Solar", "Nuclear",
                  "Hydro Run-of-River", "Hydro water reservoir", "Hydro pumped storage",
                  "Fossil gas", "Fossil hard coal", "Fossil oil", "Biomass", "Waste"]
    CONSO_COLS = ["Load", "Residual load", "Hydro pumped storage consumption"]

    gen_rows, conso_rows = [], []

    for year in range(START_YEAR, END_YEAR + 1):
        d = ec_get("public_power", f"&start={year}-01-01&end={year}-12-31")
        ts    = d["unix_seconds"]
        types = {t["name"]: t["data"] for t in d["production_types"]}

        # Resample à l'heure (l'API peut retourner du 15 min selon l'année)
        dts = ts_to_paris(ts)
        df  = pd.DataFrame({"dt": dts, **types}).set_index("dt")
        df_h = df.resample("h").mean(numeric_only=True).reset_index()

        for _, row in df_h.iterrows():
            dt   = row["dt"].to_pydatetime()
            base = {"Start date": fmt_dt(dt), "End date": fmt_dt(dt + timedelta(hours=1))}
            gen_rows.append({**base,
                **{f"{c} [MWh] Calculated resolutions": row.get(c) for c in GEN_COLS}})
            conso_rows.append({**base,
                **{f"{c} [MWh] Calculated resolutions": row.get(c) for c in CONSO_COLS}})

        print(f"    {year}: {len(ts):,} pts → {len(df_h):,} heures")
        time.sleep(0.5)

    save_csv(gen_rows,   "Actual_generation_hour.csv")
    save_csv(conso_rows, "Actual_consumption_Hour.csv")


# ─── 3. Prix day-ahead ────────────────────────────────────────────────────────
def fetch_dayahead_prices():
    print("\n[3/8] Prix day-ahead France (energy-charts.info)...")

    rows = []
    today = date.today()

    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):
            if year > today.year or (year == today.year and month > today.month):
                break
            last_day = calendar.monthrange(year, month)[1]
            start = f"{year}-{month:02d}-01"
            end   = f"{year}-{month:02d}-{last_day:02d}"

            url = f"{BASE_EC}/price?bzn={BZN}&start={start}&end={end}"
            r = requests.get(url, timeout=30, headers=HEADERS)
            r.raise_for_status()
            d = r.json()

            ts     = d.get("unix_seconds", [])
            prices = d.get("price", [])

            # Resample à l'heure si résolution 15 min (certains mois 2025)
            dts = ts_to_paris(ts)
            df_tmp = (
                pd.DataFrame({"dt": dts, "price": prices})
                .set_index("dt")
                .resample("h")
                .first()
                .reset_index()
            )
            for _, row in df_tmp.iterrows():
                dt = row["dt"].to_pydatetime()
                rows.append({
                    "Start date": fmt_dt(dt),
                    "End date":   fmt_dt(dt + timedelta(hours=1)),
                    "France [€/MWh] Calculated resolutions": row["price"],
                })

            print(f"    {year}-{month:02d}: {len(df_tmp)} heures")
            time.sleep(0.3)

    save_csv(rows, "Day-ahead_prices_hour.csv")


# ─── 4. Capacités installées ──────────────────────────────────────────────────
def fetch_installed_capacity():
    print("\n[4/8] Capacités installées (energy-charts.info)...")

    d = ec_get("installed_power", "&time_step=yearly")
    years_list  = d["time"]
    types       = {t["name"]: t["data"] for t in d["production_types"]}

    rows = []
    for year in range(START_YEAR, END_YEAR + 1):
        year_str = str(year)
        if year_str not in years_list:
            print(f"    {year}: absent du dataset")
            continue
        idx = years_list.index(year_str)

        # Capacité constante sur toute l'année (donnée annuelle → expan. horaire)
        # L'API retourne des GW → on multiplie par 1000 pour avoir des MW (cohérent avec fichiers Allemagne)
        dt = datetime(year, 1, 1, 0, 0, tzinfo=TZ)
        end_year = datetime(year + 1, 1, 1, 0, 0, tzinfo=TZ)
        count = 0
        while dt < end_year:
            row = {"Start date": fmt_dt(dt), "End date": fmt_dt(dt + timedelta(hours=1))}
            for name, vals in types.items():
                val = vals[idx] if idx < len(vals) else None
                row[f"{name} [MW] Calculated resolutions"] = round(val * 1000, 2) if val is not None else None
            rows.append(row)
            dt += timedelta(hours=1)
            count += 1
        print(f"    {year}: {count:,} heures")

    save_csv(rows, "Installed_generation_capacity_hour.csv")


# ─── 5. Flux cross-border ─────────────────────────────────────────────────────
def fetch_crossborder_flows():
    print("\n[5/8] Flux cross-border (energy-charts.info)...")

    rows = []
    for year in range(START_YEAR, END_YEAR + 1):
        d = ec_get("cbet", f"&start={year}-01-01&end={year}-12-31")
        ts        = d["unix_seconds"]
        countries = {c["name"]: c["data"] for c in d["countries"]}

        # Resample à l'heure (cbet retourne du 15 min pour France)
        dts = ts_to_paris(ts)
        df  = pd.DataFrame({"dt": dts, **countries}).set_index("dt")
        df_h = df.resample("h").mean(numeric_only=True).reset_index()

        for _, row in df_h.iterrows():
            dt = row["dt"].to_pydatetime()
            r  = {"Start date": fmt_dt(dt), "End date": fmt_dt(dt + timedelta(hours=1))}
            for name in countries:
                # L'API cbet retourne des GWh → ×1000 pour MWh (cohérent avec fichiers Allemagne)
                val = row.get(name)
                r[f"{name} (net export) [MWh] Calculated resolutions"] = (
                    round(val * 1000, 3) if val is not None and not pd.isna(val) else None
                )
            rows.append(r)

        print(f"    {year}: {len(ts):,} pts → {len(df_h):,} heures, {len(countries)} pays")
        time.sleep(0.5)

    save_csv(rows, "Cross-border_physical_flows_hour.csv")


# ─── 6. Prévision consommation (ODRÉ éCO2mix, pagination mensuelle) ──────────
def fetch_forecasted_consumption():
    print("\n[6/8] Prévision consommation (ODRÉ éCO2mix)...")

    dataset = "eco2mix-national-cons-def"
    all_records = []
    today = date.today()

    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):
            if year > today.year or (year == today.year and month > today.month):
                break
            last_day = calendar.monthrange(year, month)[1]
            # Minuit heure Paris (CET/CEST selon DST) → converti en UTC pour le filtre API
            from datetime import timezone as _tz
            first_paris = datetime(year, month, 1, 0, 0, tzinfo=TZ)
            last_paris  = datetime(year, month, last_day, 23, 30, tzinfo=TZ)
            mstart = first_paris.astimezone(_tz.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
            mend   = last_paris.astimezone(_tz.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
            wfilter = f"date_heure >= '{mstart}' AND date_heure <= '{mend}'"

            records, offset = [], 0
            while True:
                url = (
                    f"{BASE_ODRE}/{dataset}/records"
                    f"?limit=100&offset={offset}"
                    f"&where={requests.utils.quote(wfilter)}"
                    f"&select=date_heure,prevision_j,prevision_j1"
                    f"&order_by=date_heure ASC"
                )
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                batch = data.get("results", [])
                if not batch:
                    break
                records.extend(batch)
                offset += 100
                if offset >= data.get("total_count", 0):
                    break
                time.sleep(0.1)

            all_records.extend(records)
            print(f"    {year}-{month:02d}: {len(records)} enregistrements (30 min)")

    if not all_records:
        print("  ❌ Aucune donnée ODRÉ")
        return

    df = pd.DataFrame(all_records)
    df["date_heure"] = pd.to_datetime(df["date_heure"], utc=True)
    df = df.sort_values("date_heure").drop_duplicates("date_heure").reset_index(drop=True)
    # Moyenne horaire en heure Paris (gestion DST correcte)
    df_h = (
        df.set_index("date_heure")
        .tz_convert("Europe/Paris")
        .resample("h")
        .mean(numeric_only=True)
        .reset_index()
    )
    # Garder seulement les heures dans la plage START_YEAR–END_YEAR
    df_h = df_h[
        (df_h["date_heure"] >= pd.Timestamp(f"{START_YEAR}-01-01", tz="Europe/Paris")) &
        (df_h["date_heure"] <  pd.Timestamp(f"{END_YEAR+1}-01-01", tz="Europe/Paris"))
    ].reset_index(drop=True)

    rows = []
    for _, row in df_h.iterrows():
        dt = row["date_heure"].to_pydatetime()
        rows.append({
            "Start date": fmt_dt(dt),
            "End date":   fmt_dt(dt + timedelta(hours=1)),
            "Forecasted load J [MWh] Calculated resolutions":   row.get("prevision_j"),
            "Forecasted load J-1 [MWh] Calculated resolutions": row.get("prevision_j1"),
        })

    save_csv(rows, "Forecasted_consumption_hour.csv")


# ─── 7. Prévision production ENR (ren_share_forecast) ────────────────────────
def fetch_forecasted_generation():
    print("\n[7/8] Prévision production ENR (energy-charts.info / ren_share_forecast)...")
    print("  ℹ️  Donne les parts de charge (%) — pas de prévision MW directe pour FR")

    rows = []
    today = date.today()

    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):
            if year > today.year or (year == today.year and month > today.month):
                break
            last_day = calendar.monthrange(year, month)[1]
            start = f"{year}-{month:02d}-01"
            end   = f"{year}-{month:02d}-{last_day:02d}"

            url = f"{BASE_EC}/ren_share_forecast?country={COUNTRY}&start={start}&end={end}"
            r = requests.get(url, timeout=30, headers=HEADERS)
            r.raise_for_status()
            d = r.json()

            ts = d.get("unix_seconds", [])
            if not ts:
                continue

            series = {
                "Renewable share of load [%] Calculated resolutions":      d.get("ren_share", []),
                "Solar share of load [%] Calculated resolutions":          d.get("solar_share", []),
                "Wind onshore share of load [%] Calculated resolutions":   d.get("wind_onshore_share", []),
                "Wind offshore share of load [%] Calculated resolutions":  d.get("wind_offshore_share", []),
            }

            # Resample à l'heure si besoin
            dts = ts_to_paris(ts)
            n = len(ts)
            df_tmp = pd.DataFrame({"dt": dts})
            for col, vals in series.items():
                padded = (list(vals) + [None] * n)[:n] if vals else [None] * n
                df_tmp[col] = padded
            df_tmp = df_tmp.set_index("dt").resample("h").mean(numeric_only=True).reset_index()

            for _, row in df_tmp.iterrows():
                dt = row["dt"].to_pydatetime()
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=TZ)
                r_dict = {"Start date": fmt_dt(dt), "End date": fmt_dt(dt + timedelta(hours=1))}
                for col in df_tmp.columns:
                    if col != "dt":
                        r_dict[col] = row[col]
                rows.append(r_dict)

            time.sleep(0.3)
        print(f"    {year}: OK")

    save_csv(rows, "Forecasted_generation_Day-Ahead_Hour.csv")


# ─── 8. Coûts TSO (placeholder) ───────────────────────────────────────────────
def create_tso_costs_placeholder():
    print("\n[8/8] Coûts TSO (non publiés pour France — placeholder)...")

    rows = []
    for year in range(START_YEAR, END_YEAR + 1):
        dt = datetime(year, 1, 1, 0, 0, tzinfo=TZ)
        while dt.year == year:
            rows.append({
                "Start date": fmt_dt(dt),
                "End date":   fmt_dt(dt + timedelta(hours=1)),
                "Balancing services [€] Calculated resolutions":         "-",
                "Network security of the TSOs [€] Calculated resolutions": "-",
                "Countertrading [€] Calculated resolutions":             "-",
            })
            dt += timedelta(hours=1)

    save_csv(rows, "Costs_of_TSOs__without_costs_of_DSOs_hour.csv")
    print("  ℹ️  Valeurs '-' : coûts RTE non disponibles en open data")


# ─── 9. Météo (Open-Meteo) ────────────────────────────────────────────────────
def fetch_weather():
    print("\n[9/9] Météo horaire France (Open-Meteo)...")

    locations = {
        "Nord_Picardie": (50.5,  2.5),
        "Bretagne":      (48.0, -3.0),
        "Centre_Loire":  (47.5,  1.5),
        "Aquitaine":     (44.5, -0.5),
        "PACA":          (43.5,  5.5),
        "Occitanie":     (43.5,  3.0),
    }

    all_dfs = []
    for name, (lat, lon) in locations.items():
        url = (
            "https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&start_date={START_YEAR}-01-01&end_date={END_YEAR}-12-31"
            "&hourly=windspeed_10m,windspeed_100m,winddirection_100m,"
            "shortwave_radiation,direct_radiation,temperature_2m,cloudcover"
            "&timezone=Europe%2FParis&windspeed_unit=ms"
        )
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data["hourly"])
        df["time"]      = pd.to_datetime(df["time"])
        df["zone"]      = name
        df["latitude"]  = lat
        df["longitude"] = lon
        all_dfs.append(df)
        print(f"    {name}: {len(df):,} heures")
        time.sleep(0.5)

    df_all = pd.concat(all_dfs, ignore_index=True)
    out = f"{OUTPUT_DIR}/Weather_hourly_france_{START_YEAR}_{END_YEAR}.csv"
    df_all.to_csv(out, index=False)
    print(f"  ✅ Weather_hourly_france_{START_YEAR}_{END_YEAR}.csv  ({len(df_all):,} lignes)")


# ─── 10. Météo Allemagne (Open-Meteo) ────────────────────────────────────────
def fetch_weather_germany():
    print("\n[10] Météo horaire Allemagne (Open-Meteo)...")

    locations = {
        "Nordsee":            (54.5,  8.0),   # côte Nord, éolien offshore
        "Niedersachsen":      (52.8,  9.5),   # éolien onshore nord
        "Brandenburg":        (52.5, 13.5),   # éolien onshore est
        "Bayern":             (48.5, 11.5),   # solaire sud
        "Baden_Wuerttemberg": (48.0,  8.5),   # solaire sud-ouest
        "Thüringen":          (51.0, 11.0),   # centre
    }

    all_dfs = []
    for name, (lat, lon) in locations.items():
        url = (
            "https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&start_date={START_YEAR}-01-01&end_date={END_YEAR}-12-31"
            "&hourly=windspeed_10m,windspeed_100m,winddirection_100m,"
            "shortwave_radiation,direct_radiation,temperature_2m,cloudcover"
            "&timezone=Europe%2FBerlin&windspeed_unit=ms"
        )
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data["hourly"])
        df["time"]      = pd.to_datetime(df["time"])
        df["zone"]      = name
        df["latitude"]  = lat
        df["longitude"] = lon
        all_dfs.append(df)
        print(f"    {name}: {len(df):,} heures")
        time.sleep(0.5)

    df_all = pd.concat(all_dfs, ignore_index=True)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_allemagne")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"Weather_hourly_germany_{START_YEAR}_{END_YEAR}.csv")
    df_all.to_csv(out, index=False)
    print(f"  ✅ Weather_hourly_germany_{START_YEAR}_{END_YEAR}.csv  ({len(df_all):,} lignes)")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print(f"  Données France {START_YEAR}-{END_YEAR}  —  équivalent data_allemagne")
    print("  Sources : energy-charts.info + ODRÉ + Open-Meteo")
    print("=" * 65)

    fetch_public_power()
    fetch_dayahead_prices()
    fetch_installed_capacity()
    fetch_crossborder_flows()
    fetch_forecasted_consumption()
    fetch_forecasted_generation()
    create_tso_costs_placeholder()
    fetch_weather()

    print("\n" + "=" * 65)
    print(f"  Fichiers dans : {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 65)
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.endswith(".csv"):
            kb = os.path.getsize(f"{OUTPUT_DIR}/{f}") / 1024
            print(f"  {f:<55}  {kb:>7.0f} KB")
    print("=" * 65)
