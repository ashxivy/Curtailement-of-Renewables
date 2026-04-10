import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PLOTS_DIR = "plots/curtailment"

def _ensure_plots_dir():
    os.makedirs(PLOTS_DIR, exist_ok=True)

def _save_show(fig, filename):
    _ensure_plots_dir()
    path = os.path.join(PLOTS_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    return path

def _base_style(ax, title=None, xlabel=None, ylabel=None):
    if title: ax.set_title(title, fontsize=13, fontweight="bold")
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25)
    

def plot_price_distribution(df, clip=(-200, 300), bins=120, filename="price_distribution.png"):
    """Histogram of day-ahead prices (clipped)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["price"].clip(*clip), bins=bins)
    ax.axvline(0, linestyle="--", linewidth=1)
    _base_style(ax, "Price distribution", "Price [€/MWh]", "Hours")
    return _save_show(fig, filename)


def plot_curtailment_v_price_scatter(df, sample_frac=0.2, filename="curtailment_vs_price.png"):
    """Visualise la corrélation inverse entre prix et volume de curtailment."""
    df_viz = df[df["curtailment_mwh"] > 0].copy()
    if sample_frac < 1:
        df_viz = df_viz.sample(frac=sample_frac)

    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(
        df_viz["price"], 
        df_viz["curtailment_mwh"],
        c=df_viz["vre_penetration_forecast"], 
        cmap="viridis",
        alpha=0.6,
        s=30
    )
    
    ax.axvline(0, color='red', linestyle='--', alpha=0.5)
    _base_style(ax, "Curtailment Volume vs Price", "Price [€/MWh]", "Curtailment [MWh]")
    
    cbar = plt.colorbar(scatter)
    cbar.set_label("RE Penetration Forecast")
    
    return _save_show(fig, filename)

def plot_export_saturation_curtailment(df, filename="export_saturation_logic.png"):
    """Prouve que le curtailment survient quand les exports saturent."""
    # On prend les moments de fort surplus (Balance > 0)
    df_viz = df[df["generation_load_balance"] > 0].copy()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # On trace le volume d'export vs le volume de curtailment
    sns.scatterplot(
        data=df_viz,
        x="net_export_total",
        y="curtailment_mwh",
        hue="is_negative",
        palette={0: "gray", 1: "red"},
        alpha=0.5,
        ax=ax
    )
    
    _base_style(ax, "Curtailment vs Net Exports", "Net Exports [MWh]", "Curtailment [MWh]")
    return _save_show(fig, filename)

def plot_curtailment_heatmap(df, filename="curtailment_seasonal_heatmap.png"):
    """Heatmap montrant quand le curtailment est le plus fréquent (Mois vs Heure)."""
    pivot = df.pivot_table(
        index=df.index.month,
        columns=df.index.hour,
        values="curtailment_mwh",
        aggfunc="sum"
    )
    
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot, cmap="YlOrRd", cbar_kws={"label": "Total Curtailment [MWh]"}, ax=ax)
    _base_style(ax, "Temporal Intensity of Curtailment", "Hour of Day", "Month")
    return _save_show(fig, filename)

def plot_curtailment_event_zoom(df, start_date, end_date, filename="curtailment_event_zoom.png"):
    """Zoom sur une période spécifique pour voir le 'Flat-topping'."""
    d = df.loc[start_date:end_date]
    
    fig, ax1 = plt.subplots(figsize=(15, 7))
    
    # Production vs Forecast
    ax1.fill_between(d.index, d["vre_forecast_total"], d["vre_real_total"], color='red', alpha=0.3, label="Curtailed Energy")
    ax1.plot(d.index, d["vre_forecast_total"], label="VRE Potential (Forecast)", color="black", linestyle="--")
    ax1.plot(d.index, d["vre_real_total"], label="VRE Actual Production", color="green", linewidth=2)
    
    ax1.set_ylabel("Power [MW/MWh]")
    ax1.legend(loc="upper left")
    
    # Axe pour le prix
    ax2 = ax1.twinx()
    ax2.plot(d.index, d["price"], color="blue", alpha=0.6, label="Price")
    ax2.axhline(0, color='red', linewidth=1, linestyle='-')
    ax2.set_ylabel("Price [€/MWh]", color="blue")
    
    _base_style(ax1, f"Curtailment Event Detail ({start_date} to {end_date})")
    return _save_show(fig, filename)