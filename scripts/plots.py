import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('default')
import seaborn as sns


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _get_plots_dir(country: str) -> str:
    return os.path.join("plots", "curtailment", country)


def _save_show(fig, filename: str, country: str = "allemagne") -> str:
    plots_dir = _get_plots_dir(country)
    os.makedirs(plots_dir, exist_ok=True)
    path = os.path.join(plots_dir, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    return path


def _base_style(ax, title=None, xlabel=None, ylabel=None):
    if title:   ax.set_title(title, fontsize=13, fontweight="bold")
    if xlabel:  ax.set_xlabel(xlabel)
    if ylabel:  ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25)


# ─── Plots ────────────────────────────────────────────────────────────────────


def plot_curtailment_v_price_scatter(
    df,
    country: str = "allemagne",
    sample_frac=0.2,
    filename="curtailment_vs_price.png",
):
    """Corrélation inverse entre prix et volume de curtailment."""
    df_viz = df[df["curtailment_physical_economic"] > 0].copy()
    if sample_frac < 1:
        df_viz = df_viz.sample(frac=sample_frac)

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        df_viz["price"],
        df_viz["curtailment_physical_economic"],
        c=df_viz["vre_penetration_forecast"],
        cmap="viridis",
        alpha=0.6,
        s=30,
    )
    ax.axvline(0, color="red", linestyle="--", alpha=0.5)
    _base_style(ax, "Curtailment Volume vs Price", "Price [€/MWh]", "Curtailment [MWh]")
    cbar = plt.colorbar(scatter)
    cbar.set_label("RE Penetration Forecast")
    return _save_show(fig, filename, country)


def plot_weather_curtailment_conditions(
    df: pd.DataFrame,
    country: str = "allemagne",
    filename: str = "weather_curtailment_conditions.png",
):
    """
    Compare les conditions météo (vitesse vent, rayonnement solaire) pendant
    les heures avec/sans curtailment. Répond à : 'Under which conditions?'
    """
    merged = df.copy()
    curtailed = merged["is_curtailment_likely"] == 1

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # 1. Distribution vitesse vent 100 m
    ax = axes[0]
    ax.hist(merged.loc[~curtailed, "windspeed_100m"].dropna(), bins=40,
            alpha=0.6, label="Normal", density=True, color="steelblue")
    ax.hist(merged.loc[curtailed,  "windspeed_100m"].dropna(), bins=40,
            alpha=0.6, label="Curtailment", density=True, color="tomato")
    _base_style(ax, "Wind speed @ 100 m", "Wind speed [m/s]", "Density")
    ax.legend()

    # 2. Distribution rayonnement solaire
    ax = axes[1]
    ax.hist(merged.loc[~curtailed, "shortwave_radiation"].dropna(), bins=40,
            alpha=0.6, label="Normal", density=True, color="steelblue")
    ax.hist(merged.loc[curtailed,  "shortwave_radiation"].dropna(), bins=40,
            alpha=0.6, label="Curtailment", density=True, color="tomato")
    _base_style(ax, "Solar irradiation", "Shortwave radiation [W/m²]", "Density")
    ax.legend()

    # 3. Distribution température
    ax = axes[2]
    ax.hist(merged.loc[~curtailed, "temperature_2m"].dropna(), bins=40,
            alpha=0.6, label="Normal", density=True, color="steelblue")
    ax.hist(merged.loc[curtailed,  "temperature_2m"].dropna(), bins=40,
            alpha=0.6, label="Curtailment", density=True, color="tomato")
    _base_style(ax, "Temperature", "Temperature [°C]", "Density")
    ax.legend()

    fig.suptitle(f"Weather conditions during curtailment — {country.capitalize()}",
                 fontsize=14, fontweight="bold")
    return _save_show(fig, filename, country)

def plot_residual_load_vs_price(
    df,
    clip_price=(-150, 200),
    sample_frac=0.15,
    random_state=42,
    country: str = "allemagne",
):
    """Price vs residual load, colored by wind (left) and solar (right)."""
    filename=f"residual_load_vs_price_{country}.png"
    tmp = df[(df["price"] > clip_price[0]) & (df["price"] < clip_price[1])].copy()

    # échantillonnage
    if sample_frac < 1:
        tmp = tmp.sample(frac=sample_frac, random_state=random_state)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

    sns.scatterplot(
        data=tmp,
        x="residual_load",
        y="price",
        hue="wind_total",
        palette="viridis",
        alpha=0.45,
        s=20,
        ax=axes[0],
        legend=True,
    )
    axes[0].axhline(0, linestyle="--", linewidth=1, color="red")
    axes[0].axvline(0, linestyle="--", linewidth=1, color="black")
    _base_style(axes[0], "Wind effect", "Residual load [MWh]", "Price [€/MWh]")

    sns.scatterplot(
        data=tmp,
        x="residual_load",
        y="price",
        hue="solar",
        palette="plasma",
        alpha=0.45,
        s=18,
        ax=axes[1],
        legend=True,
    )
    axes[1].axhline(0, linestyle="--", linewidth=1, color="red")
    axes[1].axvline(0, linestyle="--", linewidth=1, color="black")
    _base_style(axes[1], "Solar effect", "Residual load [MWh]", None)

    fig.suptitle(f"Residual load vs price - {country.capitalize()}", fontsize=16, fontweight="bold")

    return  _save_show(fig, filename, country)


def plot_curtailment_conditions_scatter(
    df: pd.DataFrame,
    country: str = "france",
    sample_frac: float = 0.5,
    filename: str = "curtailment_conditions_scatter.png",
):
    """Montre que le curtailment survient à faible charge résiduelle et prix bas/négatifs."""
    target_var = "curtailment_physical_economic" if "curtailment_physical_economic" in df.columns else "curtailment_mwh"
    
    # On ne garde que les heures avec un écrêtement significatif
    df_viz = df[df[target_var] > 10].copy()
    if sample_frac < 1:
        df_viz = df_viz.sample(frac=sample_frac, random_state=42)

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        df_viz["residual_load"],
        df_viz["price"],
        c=df_viz[target_var],
        cmap="viridis",
        alpha=0.6,
        s=40,
    )
    
    # Lignes de repère pour le zéro
    ax.axhline(0, color="red", linestyle="--", alpha=0.8, linewidth=1.5, label="Zero Price")
    ax.axvline(0, color="black", linestyle="--", alpha=0.5, linewidth=1)
    
    _base_style(ax, f"Conditions of Curtailment — {country.capitalize()}", "Residual Load [MWh]", "Day-Ahead Price [€/MWh]")
    ax.legend(loc="upper left")
    
    cbar = plt.colorbar(scatter)
    cbar.set_label("Curtailed Volume [MWh]")
    return _save_show(fig, filename, country)


def plot_price_distribution(
        df,
        country: str = "allemagne",
        clip=(-200, 300),
        bins=120,
        filename="price_distribution.png",
):
    """Histogramme des prix day-ahead (écrêté)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["price"].clip(*clip), bins=bins)
    ax.axvline(0, linestyle="--", linewidth=1)
    _base_style(ax, "Price distribution", "Price [€/MWh]", "Hours")
    return _save_show(fig, filename, country)


def plot_export_saturation_curtailment(
        df,
        country: str = "allemagne",
        filename="export_saturation_logic.png",
):
    """Montre que le curtailment survient quand les exports saturent."""
    df_viz = df[df["generation_load_balance"] > 0].copy()

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.scatterplot(
        data=df_viz,
        x="net_export_total",
        y="curtailment_physical_economic",
        hue="is_negative",
        palette={0: "gray", 1: "red"},
        alpha=0.5,
        ax=ax,
    )
    _base_style(ax, "Curtailment vs Net Exports", "Net Exports [MWh]", "Curtailment [MWh]")
    return _save_show(fig, filename, country)


def plot_curtailment_heatmap(
        df: pd.DataFrame,
        country: str = "france",
        filename: str = "curtailment_seasonal_heatmap.png",
):
    """Heatmap Mois × Heure de la fréquence du curtailment physique."""
    # On utilise la nouvelle variable d'écrêtement physique !
    target_var = "curtailment_physical_economic" if "curtailment_physical_economic" in df.columns else "curtailment_mwh"

    pivot = df.pivot_table(
        index=df.index.month,
        columns=df.index.hour,
        values=target_var,
        aggfunc="sum",
    )
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot, cmap="YlOrRd", cbar_kws={"label": f"Total Curtailment [MWh]"}, ax=ax)

    # On renomme proprement l'axe des Y pour les mois
    ax.set_yticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], rotation=0)

    _base_style(ax, f"Temporal Intensity of Curtailment — {country.capitalize()}", "Hour of Day", "Month")
    return _save_show(fig, filename, country)


def plot_curtailment_prob_by_wind(
        df: pd.DataFrame,
        country: str = "allemagne",
        filename: str = "curtailment_prob_vs_wind.png",
):
    """
    Probabilité de curtailment en fonction de la vitesse du vent (binée).
    Répond à : 'Under which conditions?' et 'For which renewables?'
    """
    merged = df.dropna(subset=["windspeed_100m", "is_curtailment_likely"])
    merged["wind_bin"] = pd.cut(merged["windspeed_100m"], bins=range(0, 22, 2))
    stats = (
        merged.groupby("wind_bin", observed=True)["is_curtailment_likely"]
        .agg(prob="mean", count="size")
        .reset_index()
    )

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()

    ax1.bar(range(len(stats)), stats["prob"] * 100, color="tomato", alpha=0.8,
            label="P(curtailment) [%]")
    ax2.plot(range(len(stats)), stats["count"], "o--", color="navy", alpha=0.7,
             label="Nombre d'heures")

    ax1.set_xticks(range(len(stats)))
    ax1.set_xticklabels([str(b) for b in stats["wind_bin"]], rotation=45, ha="right")
    _base_style(ax1, f"Curtailment probability vs wind speed — {country.capitalize()}",
                "Wind speed bin [m/s]", "P(curtailment) [%]")
    ax2.set_ylabel("Number of hours", color="navy")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    return _save_show(fig, filename, country)


def plot_curtailment_prob_by_temperature(
        df: pd.DataFrame,
        country: str = "allemagne",
        filename: str = "curtailment_prob_vs_temperature.png",
):
    """
    Probabilité de curtailment en fonction de la température (binée par tranche de 5°C).
    """
    merged = df.dropna(subset=["temperature_2m", "is_curtailment_likely"])
    merged["temp_bin"] = pd.cut(merged["temperature_2m"], bins=range(-15, 40, 5))
    stats = (
        merged.groupby("temp_bin", observed=True)["is_curtailment_likely"]
        .agg(prob="mean", count="size")
        .reset_index()
    )

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()

    ax1.bar(range(len(stats)), stats["prob"] * 100, color="steelblue", alpha=0.8,
            label="P(curtailment) [%]")
    ax2.plot(range(len(stats)), stats["count"], "o--", color="tomato", alpha=0.7,
             label="Nombre d'heures")

    ax1.set_xticks(range(len(stats)))
    ax1.set_xticklabels([str(b) for b in stats["temp_bin"]], rotation=45, ha="right")
    _base_style(ax1, f"Curtailment probability vs temperature — {country.capitalize()}",
                "Temperature bin [°C]", "P(curtailment) [%]")
    ax2.set_ylabel("Number of hours", color="tomato")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    return _save_show(fig, filename, country)


def plot_curtailment_by_renewable_type(
        df: pd.DataFrame,
        country: str = "allemagne",
        filename: str = "curtailment_by_renewable_type.png",
):
    """
    Décompose le curtailment par type de renouvelable (éolien vs solaire)
    et par mois. Répond à : 'For which renewables?'
    Proxy : curtailment diurne (6h-20h) → solaire ; nocturne → éolien.
    """
    d = df[df["is_curtailment_likely"] == 1].copy()
    d["month"] = d.index.month
    d["is_daytime"] = ((d.index.hour >= 6) & (d.index.hour < 20)).astype(int)

    monthly = d.groupby(["month", "is_daytime"])["curtailment_mwh"].sum().unstack(fill_value=0)

    # Sécurité si une des deux colonnes manque
    monthly = monthly.reindex(columns=[0, 1], fill_value=0)
    monthly.columns = ["Nuit (éolien)", "Jour (solaire + éolien)"]

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Barres empilées par mois
    ax = axes[0]
    monthly.plot(kind="bar", stacked=True, ax=ax,
                 color=["steelblue", "gold"], alpha=0.85)

    _base_style(ax, f"Curtailment by month & time-of-day — {country.capitalize()}",
                "Month", "Curtailment [MWh]")

    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    ax.set_xticklabels(
        [month_labels[m - 1] for m in monthly.index],
        rotation=45
    )

    ax.legend()

    # Pie chart global nuit/jour
    ax = axes[1]
    totals = monthly.sum()
    ax.pie(totals, labels=totals.index, autopct="%1.1f%%",
           colors=["steelblue", "gold"], startangle=90)

    ax.set_title(f"Curtailment split: day vs night\n{country.capitalize()}",
                 fontsize=12, fontweight="bold")

    return _save_show(fig, filename, country)


def plot_curtailment_wind_solar_scatter(
        df: pd.DataFrame,
        country: str = "allemagne",
        filename: str = "curtailment_wind_solar_map.png",
):
    """
    Scatter 2D vitesse vent × rayonnement solaire, coloré par intensité du curtailment.
    Montre la zone météo à risque.
    """
    merged = df.copy()
    sample = merged.sample(min(5000, len(merged)), random_state=42)

    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(
        sample["windspeed_100m"],
        sample["shortwave_radiation"],
        c=sample["curtailment_mwh"].clip(upper=sample["curtailment_mwh"].quantile(0.99)),
        cmap="YlOrRd",
        alpha=0.5,
        s=15,
    )
    cbar = plt.colorbar(sc)
    cbar.set_label("Curtailment [MWh]")
    _base_style(ax,
                f"Curtailment intensity: wind vs solar conditions — {country.capitalize()}",
                "Wind speed @ 100 m [m/s]",
                "Solar irradiation [W/m²]")
    return _save_show(fig, filename, country)


def plot_curtailment_event_zoom(
        df,
        start_date,
        end_date,
        country: str = "allemagne",
        filename="curtailment_event_zoom.png",
):
    """Zoom sur un événement de curtailment (flat-topping)."""
    d = df.loc[start_date:end_date]

    fig, ax1 = plt.subplots(figsize=(15, 7))
    ax1.fill_between(
        d.index, d["vre_forecast_total"], d["vre_real_total"],
        color="red", alpha=0.3, label="Curtailed Energy",
    )
    ax1.plot(d.index, d["vre_forecast_total"], label="VRE Potential (Forecast)",
             color="black", linestyle="--")
    ax1.plot(d.index, d["vre_real_total"], label="VRE Actual Production",
             color="green", linewidth=2)
    ax1.set_ylabel("Power [MWh]")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(d.index, d["price"], color="blue", alpha=0.6, label="Price")
    ax2.axhline(0, color="red", linewidth=1, linestyle="-")
    ax2.set_ylabel("Price [€/MWh]", color="blue")

    _base_style(ax1, f"Curtailment Event Detail ({start_date} to {end_date})")
    return _save_show(fig, filename, country)


def plot_curtailment_conditions_scatter(
    df: pd.DataFrame,
    country: str = "france",
    sample_frac: float = 0.5,
    filename: str = "curtailment_conditions_scatter_pct.png",
):
    """
    Scatter plot :
    x = residual load
    y = price
    couleur = curtailment [% of theoretical VRE]
    """

    target_var = (
        "curtailment_physical_economic"
        if "curtailment_physical_economic" in df.columns
        else "curtailment_mwh"
    )

    d = df.copy()

    # Curtailment en % de la production renouvelable théorique disponible
    d["curtailment_pct"] = (
        100 * d[target_var] / d["vre_theoretical_total"].replace(0, np.nan)
    )

    # On garde seulement les heures avec un écrêtement significatif
    df_viz = d[d[target_var] > 10].copy()

    df_viz = df_viz.dropna(
        subset=["curtailment_pct", "price", "residual_load"]
    )

    # Sécurité : un pourcentage doit être entre 0 et 100
    df_viz["curtailment_pct"] = df_viz["curtailment_pct"].clip(lower=0, upper=100)

    if sample_frac < 1:
        df_viz = df_viz.sample(frac=sample_frac, random_state=42)

    fig, ax = plt.subplots(figsize=(10, 6))

    scatter = ax.scatter(
        df_viz["residual_load"],
        df_viz["price"],
        c=df_viz["curtailment_pct"],
        cmap="viridis",
        alpha=0.6,
        s=40,
    )

    # Lignes de repère pour le zéro
    ax.axhline(
        0,
        color="red",
        linestyle="--",
        alpha=0.8,
        linewidth=1.5,
        label="Zero Price",
    )

    ax.axvline(
        0,
        color="black",
        linestyle="--",
        alpha=0.5,
        linewidth=1,
        label="Zero Residual Load",
    )

    _base_style(
        ax,
        f"Conditions of Curtailment — {country.capitalize()}",
        "Residual Load [MWh]",
        "Day-Ahead Price [€/MWh]",
    )

    ax.legend(loc="upper left")

    cbar = plt.colorbar(scatter)
    cbar.set_label("Curtailment [% of theoretical VRE]")

    return _save_show(fig, filename, country)

def plot_curtailment_two_scatters(
    df: pd.DataFrame,
    country: str = "france",
    sample_frac: float = 0.5,
    filename: str = "curtailment_two_scatters_pct.png",
):
    """
    Deux scatter plots distincts :
    (i) curtailment [%] vs price
    (ii) curtailment [%] vs residual load

    Curtailment [%] = curtailment_physical_economic / VRE theoretical potential
    """

    target_var = (
        "curtailment_physical_economic"
        if "curtailment_physical_economic" in df.columns
        else "curtailment_mwh"
    )

    d = df.copy()

    # Dénominateur le plus logique : production VRE potentielle théorique
    d["curtailment_pct"] = (
        100 * d[target_var] / d["vre_theoretical_total"].replace(0, np.nan)
    )

    # On garde seulement les heures avec écrêtement significatif
    d = d[d[target_var] > 10].dropna(
        subset=["curtailment_pct", "price", "residual_load"]
    )

    # Sécurité : un % doit être entre 0 et 100
    d["curtailment_pct"] = d["curtailment_pct"].clip(lower=0, upper=100)

    if sample_frac < 1:
        d = d.sample(frac=sample_frac, random_state=42)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # (i) Curtailment % vs Price
    axes[0].scatter(
        d["price"],
        d["curtailment_pct"],
        alpha=0.6,
        s=40,
    )

    axes[0].axvline(
        0,
        color="red",
        linestyle="--",
        alpha=0.8,
        linewidth=1.5,
        label="Zero Price",
    )

    _base_style(
        axes[0],
        f"Curtailment Share vs Price — {country.capitalize()}",
        "Day-Ahead Price [€/MWh]",
        "Curtailment [% of theoretical VRE]",
    )

    axes[0].legend(loc="upper right")

    # (ii) Curtailment % vs Residual Load
    axes[1].scatter(
        d["residual_load"],
        d["curtailment_pct"],
        alpha=0.6,
        s=40,
    )

    axes[1].axvline(
        0,
        color="black",
        linestyle="--",
        alpha=0.5,
        linewidth=1,
        label="Zero Residual Load",
    )

    _base_style(
        axes[1],
        f"Curtailment Share vs Residual Load — {country.capitalize()}",
        "Residual Load [MWh]",
        "Curtailment [% of theoretical VRE]",
    )

    axes[1].legend(loc="upper right")

    fig.suptitle(
        f"Curtailment conditions — {country.capitalize()}",
        fontsize=15,
        fontweight="bold",
    )

    return _save_show(fig, filename, country)


def plot_combined_curtailment_analysis(
    df: pd.DataFrame,
    country: str = "france",
    filename: str = "combined_curtailment_analysis.png",
):
    """
    Analyse combinée :
    1. Barres empilées mensuelles par source (Vent/Soleil).
    2. Heatmap temporelle (Mois x Heure).
    """

    wind_col = "curtailment_physical_wind"
    solar_col = "curtailment_physical_solar"
    target_var = "curtailment_physical_economic"

    if not all(c in df.columns for c in [wind_col, solar_col, target_var]):
        print("Erreur : Colonnes physiques manquantes.")
        return None

    monthly_src = df.groupby(df.index.month)[[wind_col, solar_col]].sum()
    monthly_src.columns = ["Wind Curtailment", "Solar Curtailment"]

    heatmap_data = df.pivot_table(
        index=df.index.month,
        columns=df.index.hour,
        values=target_var,
        aggfunc="sum"
    )

    fig, axes = plt.subplots(1, 2, figsize=(18, 7),
                             gridspec_kw={'width_ratios': [1, 1.2]})

    # Barres empilées
    ax1 = axes[0]
    monthly_src.plot(kind="bar", stacked=True, ax=ax1,
                     color=["#4b8bbe", "#ffcc00"], alpha=0.9)

    _base_style(ax1, "Monthly Curtailment Volume by Source", "Month", "Volume [MWh]")

    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]

    ax1.set_xticklabels(
        [month_labels[m - 1] for m in monthly_src.index],
        rotation=45
    )

    ax1.legend()

    # Heatmap
    ax2 = axes[1]
    sns.heatmap(heatmap_data, cmap="YlOrRd", ax=ax2,
                cbar_kws={'label': 'Total Curtailment [MWh]'})

    ax2.set_yticklabels(
        [month_labels[m - 1] for m in heatmap_data.index],
        rotation=0
    )

    _base_style(ax2, "Curtailment Intensity (Hour vs Month)", "Hour of Day", "Month")

    return _save_show(fig, filename, country)

def plot_export_congestion_analysis(
    df,
    clip_price=(-150, 200),
    sample_frac=0.15,
    random_state=42,
    country: str = "allemagne",
):
    """
    Prix en fonction des exports nets
    Couleur : prix moyen des pays voisins
    """
    filename=f"exports_and_price_{country}.png"
    df_viz = df.copy()

    neighbor_cols = [c for c in df_viz.columns if "price_" in c and c != "price"]

    if neighbor_cols:
        df_viz["mean_neighbor_price"] = df_viz[neighbor_cols].mean(axis=1)
    else:
        df_viz["mean_neighbor_price"] = 0

    df_viz = df_viz[(df_viz["price"] > clip_price[0]) & (df_viz["price"] < clip_price[1])]

    # échantillonnage
    if sample_frac < 1:
        df_viz = df_viz.sample(frac=sample_frac, random_state=random_state)

    fig = plt.figure(figsize=(12, 7))
    ax = plt.gca()

    sns.scatterplot(
        data=df_viz,
        x="net_export_total",
        y="price",
        hue="mean_neighbor_price",
        palette="coolwarm",
        hue_norm=(-50, 100),
        alpha=0.7,
        s=20,
        ax=ax,
        legend=False,
    )

    plt.axhline(0, color="black", linewidth=1)
    plt.axvline(0, color="gray", linestyle="--")

    plt.title(f"Exports, Congestion and Price Contagion - {country.capitalize()}", fontsize=16)
    plt.xlabel("Net Exports [MWh]  (>0 export | <0 import)")
    plt.ylabel(f"{country} Price [€/MWh]")

    sm = plt.cm.ScalarMappable(cmap="coolwarm", norm=plt.Normalize(-50, 100))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Average Neighbor Price [€/MWh]")

    plt.grid(True, alpha=0.3)

    return _save_show(fig, filename, country)

def plot_negative_price_import_concomitance(
    df: pd.DataFrame,
    country: str = "france",
    filename: str = "negative_price_import_concomitance.png",
):
    """
    Analyse les épisodes où la France importe malgré un prix négatif.
    Si le prix voisin moyen est encore plus bas que le prix français,
    cela suggère que le prix négatif peut être 'importé'.
    """

    d = df.copy()

    # Colonnes de prix voisins
    neighbor_cols = [c for c in d.columns if c.startswith("price_") and c != "price"]

    if not neighbor_cols:
        print("Aucune colonne de prix voisin trouvée.")
        return None

    # Prix moyen des voisins
    d["mean_neighbor_price"] = d[neighbor_cols].mean(axis=1)

    # Spread : prix France - prix voisins
    # Si > 0, les voisins sont moins chers / plus négatifs
    d["price_spread_neighbor"] = d["price"] - d["mean_neighbor_price"]

    # Cas d'intérêt : prix négatif en France + imports
    d["negative_price"] = d["price"] < 0
    d["importing"] = d["net_export_total"] < 0

    d_event = d[d["negative_price"] & d["importing"]].copy()

    if d_event.empty:
        print("Aucun épisode trouvé : prix négatif + import.")
        return None

    # Classification
    d_event["imported_negative_price"] = d_event["price_spread_neighbor"] > 0

    share_imported = 100 * d_event["imported_negative_price"].mean()

    fig, ax = plt.subplots(figsize=(10, 6))

    scatter = ax.scatter(
        d_event["mean_neighbor_price"],
        d_event["price"],
        c=d_event["net_export_total"],
        cmap="coolwarm",
        alpha=0.7,
        s=35,
    )

    # Ligne y = x
    min_price = min(d_event["price"].min(), d_event["mean_neighbor_price"].min())
    max_price = max(d_event["price"].max(), d_event["mean_neighbor_price"].max())

    ax.plot(
        [min_price, max_price],
        [min_price, max_price],
        color="black",
        linestyle="--",
        linewidth=1,
        label="France price = neighbor price",
    )

    ax.axhline(0, color="red", linestyle=":", linewidth=1)
    ax.axvline(0, color="red", linestyle=":", linewidth=1)

    _base_style(
        ax,
        f"Negative Prices while Importing — {country.capitalize()}",
        "Germany price [€/MWh]",
        f"{country.capitalize()} price [€/MWh]",
    )

    cbar = plt.colorbar(scatter)
    cbar.set_label("Net exports [MWh] (<0 = imports)")

    ax.legend(loc="upper left")

    ax.text(
        0.02,
        0.02,
        f"{share_imported:.1f}% of negative-price import hours\nhave neighbors cheaper than France",
        transform=ax.transAxes,
        fontsize=11,
        bbox=dict(facecolor="white", alpha=0.8),
    )

    return _save_show(fig, filename, country)

def plot_curtailment_comparison_with_price(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    country: str = "france",
    filename: str = "curtailment_method_comparison_price.png",
):
    """
    Compare les deux méthodes de calcul de l'écrêtement sur une période donnée,
    en superposant la courbe des prix pour vérifier la corrélation avec les prix négatifs.
    """
    # Sélection de la période
    d = df.loc[start_date:end_date].copy()
    
    col_market = "curtailment_mwh" if "curtailment_mwh" in d.columns else "curtailment_raw_gap"
    col_physical = "curtailment_physical_economic"
    
    fig, ax1 = plt.subplots(figsize=(15, 7))
    
    # --- Axe Principal (Gauche) : Les volumes d'écrêtement ---
    ax1.plot(d.index, d[col_physical], label="Physical Curtailment (Weather-based)", color="tomato", linewidth=2.5)
    ax1.plot(d.index, d[col_market], label="Market Curtailment (Forecast-based)", color="steelblue", linewidth=2.5)
    
    # Zone de remplissage
    fill = ax1.fill_between(d.index, d[col_market], d[col_physical], 
                            color="tomato", alpha=0.15, label="Anticipated Curtailment (Endogenized)")
    
    ax1.set_ylabel("Curtailment Volume [MWh]", color="black", fontsize=11)
    
    # --- Axe Secondaire (Droite) : Le Prix Day-Ahead ---
    if "price" in d.columns:
        ax2 = ax1.twinx()
        
        # Courbe des prix
        ax2.plot(d.index, d["price"], label="Day-Ahead Price", color="purple", linewidth=1.5, linestyle="--", alpha=0.8)
        ax2.set_ylabel("Price [€/MWh]", color="purple", fontsize=11)
        ax2.tick_params(axis='y', labelcolor="purple")
        
        # Ligne rouge pointillée horizontale à ZÉRO pour le prix
        ax2.axhline(0, color="red", linestyle=":", linewidth=2, alpha=0.7, label="Zero Price Line")
        
        # Légende de l'axe de droite (Prix)
        ax2.legend(loc="upper right", fontsize=10)
    
    # --- Formattage global ---
    # On met None pour le ylabel dans _base_style car on vient de le définir manuellement pour ax1 et ax2
    _base_style(ax1, 
                f"Curtailment vs Price ({start_date} to {end_date}) — {country.capitalize()}", 
                "Date", 
                None)
    
    # Légende de l'axe de gauche (Volumes)
    ax1.legend(loc="upper left", fontsize=10)
    
    return _save_show(fig, filename, country)

def plot_mix_during_curtailment(df, country="france"):
    """
    Montre la part des autres sources (Nucléaire, Thermique) 
    quand l'écrêtement est au maximum.
    """
    # On prend les 5% des heures où l'écrêtement physique est le plus fort
    threshold = df["curtailment_physical_economic"].quantile(0.95)
    high_curt = df[df["curtailment_physical_economic"] > threshold].copy()
    
    # On agrège les catégories de production
    mix_cols = ["nuclear", "gas", "coal", "lignite", "hydro", "vre_real_total"]
    available_cols = [c for c in mix_cols if c in high_curt.columns]
    
    mean_gen = high_curt[available_cols].mean()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    mean_gen.plot(kind='bar', ax=ax, color='teal')
    
    _base_style(ax, f"Average Generation Mix during High Curtailment \n (5% hours with the highest physical Curtailment) — {country.capitalize()}", 
                "Source", "Average Generation [MWh]")
    return _save_show(fig, f"mix_during_curtailment_{country}.png", country)