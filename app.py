"""
========================================================================================
 AutoSTAT — Dashboard statistique & détermination automatique des types de variables
========================================================================================
Application Streamlit complète pour la fiche TP « Statistique descriptive » (2025-2026) :

  • détection automatique des types de variables (Listing 3)
  • tableaux statistiques et représentations graphiques (Listings 4 à 6)
  • paramètres de position, de dispersion et de forme (Listing 7)
  • interpolation linéaire sur histogramme (Listings 10 et 11)
  • courbe cumulative et lecture des quantiles Me, Q1, Q2, Q3, D6 (Listing 12)
  • diagramme de Tukey et détection des points aberrants (Listings 16 à 20)
  • discrétisation discret -> continu (Listing 21)
  • opération inverse : graphique -> tableau (Listings 21 à 23)
  • dashboard de synthèse et exercices supplémentaires (Section 16 de la fiche)

Interface : thème sombre / clair commutable, composants CSS personnalisés,
graphiques Plotly thémés, tableaux HTML soignés.
========================================================================================
"""

from __future__ import annotations

import html as _html
from string import Template

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# Configuration de la page
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AutoSTAT · Dashboard statistique",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Thèmes (sombre / clair) — palette CSS + palette graphique Plotly
# -----------------------------------------------------------------------------
THEMES = {
    "dark": {
        "css": {
            "primary": "#6366f1",
            "primary_strong": "#4338ca",
            "primary_soft": "rgba(99, 102, 241, 0.16)",
            "accent": "#22d3ee",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "bg": "#0a1020",
            "surface": "#111a2f",
            "surface_2": "#16223c",
            "border": "rgba(148, 163, 184, 0.16)",
            "text": "#e8eefc",
            "muted": "#93a4be",
            "shadow": "0 24px 60px -30px rgba(2, 6, 23, 0.95)",
            "grid": "rgba(148, 163, 184, 0.14)",
            "glow1": "rgba(99, 102, 241, 0.22)",
            "glow2": "rgba(34, 211, 238, 0.14)",
            "sidebar_bg": "rgba(13, 20, 38, 0.94)",
            "hero_a": "rgba(99, 102, 241, 0.24)",
            "hero_b": "rgba(34, 211, 238, 0.14)",
            "hero_c": "rgba(16, 185, 129, 0.10)",
            "hero_from": "#ffffff",
            "hero_to": "#a5b4fc",
            "row_alt": "rgba(148, 163, 184, 0.05)",
            "row_hover": "rgba(99, 102, 241, 0.13)",
            "success_bg": "rgba(16, 185, 129, 0.09)",
            "warn_bg": "rgba(245, 158, 11, 0.09)",
            "danger_bg": "rgba(239, 68, 68, 0.09)",
            "scroll": "rgba(148, 163, 184, 0.35)",
            "b_blue": "#60a5fa",
            "b_violet": "#c084fc",
            "b_green": "#34d399",
            "b_amber": "#fbbf24",
            "b_gray": "#94a3b8",
        },
        "chart": {
            "font": "#c7d2e4",
            "title": "#e8eefc",
            "grid": "rgba(148, 163, 184, 0.14)",
            "colorway": ["#818cf8", "#22d3ee", "#34d399", "#fbbf24", "#fb7185", "#a78bfa"],
            "hover_bg": "#16223c",
            "pie_line": "#0a1020",
        },
    },
    "light": {
        "css": {
            "primary": "#4f46e5",
            "primary_strong": "#4338ca",
            "primary_soft": "rgba(79, 70, 229, 0.10)",
            "accent": "#0891b2",
            "success": "#059669",
            "warning": "#d97706",
            "danger": "#dc2626",
            "bg": "#f4f6fb",
            "surface": "#ffffff",
            "surface_2": "#eef2f9",
            "border": "rgba(15, 23, 42, 0.10)",
            "text": "#0f172a",
            "muted": "#5b6b85",
            "shadow": "0 24px 60px -34px rgba(15, 23, 42, 0.35)",
            "grid": "rgba(15, 23, 42, 0.08)",
            "glow1": "rgba(99, 102, 241, 0.13)",
            "glow2": "rgba(6, 182, 212, 0.10)",
            "sidebar_bg": "rgba(255, 255, 255, 0.94)",
            "hero_a": "#eef2ff",
            "hero_b": "#e0f7fb",
            "hero_c": "#ecfdf5",
            "hero_from": "#1e1b4b",
            "hero_to": "#4f46e5",
            "row_alt": "rgba(15, 23, 42, 0.025)",
            "row_hover": "rgba(79, 70, 229, 0.08)",
            "success_bg": "#ecfdf5",
            "warn_bg": "#fffbeb",
            "danger_bg": "#fef2f2",
            "scroll": "rgba(15, 23, 42, 0.25)",
            "b_blue": "#1d4ed8",
            "b_violet": "#7c3aed",
            "b_green": "#047857",
            "b_amber": "#b45309",
            "b_gray": "#475569",
        },
        "chart": {
            "font": "#475569",
            "title": "#0f172a",
            "grid": "rgba(15, 23, 42, 0.08)",
            "colorway": ["#4f46e5", "#0891b2", "#059669", "#d97706", "#e11d48", "#7c3aed"],
            "hover_bg": "#ffffff",
            "pie_line": "#ffffff",
        },
    },
}

CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary: ${primary};
    --primary-strong: ${primary_strong};
    --primary-soft: ${primary_soft};
    --accent: ${accent};
    --success: ${success};
    --warning: ${warning};
    --danger: ${danger};
    --bg: ${bg};
    --surface: ${surface};
    --surface-2: ${surface_2};
    --border: ${border};
    --text: ${text};
    --muted: ${muted};
    --shadow: ${shadow};

    /* Passerelle vers le thème natif Streamlit */
    --primary-color: ${primary};
    --background-color: ${bg};
    --secondary-background-color: ${surface};
    --text-color: ${text};
}

html, body, [data-testid="stAppViewContainer"], [class*="css"] {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

code, pre, .mono { font-family: 'JetBrains Mono', ui-monospace, monospace !important; }

.stApp {
    background:
        radial-gradient(1100px 520px at 12% -12%, ${glow1} 0%, transparent 62%),
        radial-gradient(900px 480px at 108% -4%, ${glow2} 0%, transparent 58%),
        var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1320px; }

/* ---------------- Barre latérale ---------------- */
[data-testid="stSidebar"] {
    background: ${sidebar_bg};
    border-right: 1px solid var(--border);
    backdrop-filter: blur(16px);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }

.brand {
    display: flex; align-items: center; gap: 12px;
    padding: 6px 2px 16px;
}
.brand-logo {
    width: 46px; height: 46px; border-radius: 15px; display: grid; place-items: center;
    font-size: 1.45rem;
    background: linear-gradient(145deg, var(--primary), var(--primary-strong));
    box-shadow: 0 14px 30px -16px var(--primary);
}
.brand-name { font-size: 1.22rem; font-weight: 700; letter-spacing: -0.01em; color: var(--text); line-height: 1.1; }
.brand-sub { font-size: 0.72rem; color: var(--muted); letter-spacing: 0.04em; }

.side-title {
    font-size: 0.66rem; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--muted); font-weight: 700; margin: 16px 0 6px;
}
.divider { height: 1px; background: var(--border); margin: 16px 0; }

/* ---------------- En-tête hero ---------------- */
.hero {
    position: relative; overflow: hidden;
    border: 1px solid var(--border); border-radius: 22px;
    padding: 26px 30px 22px; margin-bottom: 22px;
    background: linear-gradient(135deg, ${hero_a} 0%, ${hero_b} 52%, ${hero_c} 100%);
    box-shadow: var(--shadow);
    animation: rise 0.45s ease-out both;
}
.hero::after {
    content: ''; position: absolute; inset: 0; pointer-events: none;
    background-image:
        linear-gradient(${grid} 1px, transparent 1px),
        linear-gradient(90deg, ${grid} 1px, transparent 1px);
    background-size: 36px 36px;
    mask-image: radial-gradient(circle at 74% 16%, #000 0%, transparent 72%);
    -webkit-mask-image: radial-gradient(circle at 74% 16%, #000 0%, transparent 72%);
    opacity: 0.55;
}
.hero-top { position: relative; z-index: 1; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px; }
.hero-eyebrow { font-size: 0.68rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
.hero-title {
    margin: 6px 0 0; font-size: 2rem; line-height: 1.15; font-weight: 700; letter-spacing: -0.02em;
    background: linear-gradient(90deg, ${hero_from} 0%, ${hero_to} 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub { margin: 8px 0 0; color: var(--muted); font-size: 0.95rem; max-width: 780px; }
.hero-chips { position: relative; z-index: 1; display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 12px; border-radius: 999px;
    background: var(--surface); border: 1px solid var(--border);
    color: var(--muted); font-size: 0.76rem; font-weight: 500;
    max-width: 340px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* ---------------- Titres de section ---------------- */
.section-head { display: flex; align-items: center; gap: 14px; margin: 4px 0 18px; }
.section-ico {
    width: 46px; height: 46px; flex: 0 0 46px; border-radius: 15px;
    display: grid; place-items: center; font-size: 1.25rem;
    background: var(--primary-soft); border: 1px solid var(--border);
}
.section-head h2 { margin: 0; font-size: 1.38rem; font-weight: 700; letter-spacing: -0.01em; color: var(--text); }
.section-head p { margin: 3px 0 0; color: var(--muted); font-size: 0.85rem; }
.mini-title {
    font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--muted); font-weight: 700; margin: 6px 0 10px;
}

/* ---------------- Badges de type ---------------- */
.badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 12px; border-radius: 999px;
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em;
    text-transform: uppercase; border: 1px solid transparent; white-space: nowrap;
}
.badge-blue   { background: rgba(59, 130, 246, 0.16);  color: ${b_blue};   border-color: rgba(59, 130, 246, 0.38); }
.badge-violet { background: rgba(168, 85, 247, 0.16);  color: ${b_violet}; border-color: rgba(168, 85, 247, 0.38); }
.badge-green  { background: rgba(16, 185, 129, 0.16);  color: ${b_green};  border-color: rgba(16, 185, 129, 0.38); }
.badge-amber  { background: rgba(245, 158, 11, 0.16);  color: ${b_amber};  border-color: rgba(245, 158, 11, 0.38); }
.badge-gray   { background: rgba(148, 163, 184, 0.16); color: ${b_gray};   border-color: rgba(148, 163, 184, 0.38); }

/* ---------------- Cartes KPI ---------------- */
.kpi {
    position: relative; overflow: hidden; height: 100%;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 15px 18px;
    transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    animation: rise 0.4s ease-out both;
}
.kpi::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: linear-gradient(var(--primary), var(--accent));
}
.kpi:hover { transform: translateY(-3px); border-color: var(--primary); box-shadow: 0 18px 32px -24px var(--primary); }
.kpi-label { font-size: 0.7rem; letter-spacing: 0.09em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
.kpi-value { font-size: 1.5rem; font-weight: 700; color: var(--text); margin-top: 4px; line-height: 1.2; font-variant-numeric: tabular-nums; }
.kpi-sub { font-size: 0.74rem; color: var(--muted); margin-top: 3px; }

/* ---------------- Callouts ---------------- */
.callout {
    display: flex; gap: 12px; align-items: flex-start;
    border: 1px solid var(--border); border-left: 4px solid var(--primary);
    border-radius: 0 14px 14px 0; background: var(--surface);
    padding: 13px 16px; margin: 12px 0;
}
.callout.success { border-left-color: var(--success); background: ${success_bg}; }
.callout.warn    { border-left-color: var(--warning); background: ${warn_bg}; }
.callout.danger  { border-left-color: var(--danger);  background: ${danger_bg}; }
.co-ico { font-size: 1.05rem; line-height: 1.35; }
.co-title { font-weight: 700; color: var(--text); font-size: 0.9rem; }
.co-body { color: var(--muted); font-size: 0.86rem; line-height: 1.55; margin-top: 2px; }
.co-body b, .co-body strong { color: var(--text); }
.co-body code { background: var(--surface-2); border-radius: 6px; padding: 1px 5px; font-size: 0.8rem; }

/* ---------------- Formules (KaTeX) ---------------- */
.katex-display {
    background: var(--surface-2); border: 1px solid var(--border);
    border-left: 4px solid var(--accent); border-radius: 0 14px 14px 0;
    padding: 10px 16px; margin: 10px 0 !important; overflow-x: auto;
}
.katex { color: var(--text); }

/* ---------------- Tableaux HTML ---------------- */
.tbl-wrap {
    overflow: auto; max-height: 460px;
    border: 1px solid var(--border); border-radius: 14px;
    background: var(--surface);
}
table.tp-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
table.tp-table thead th {
    position: sticky; top: 0; z-index: 2;
    background: var(--surface-2); color: var(--muted);
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em;
    text-transform: uppercase; text-align: center; white-space: nowrap;
    padding: 10px 12px; border-bottom: 1px solid var(--border);
}
table.tp-table tbody td {
    padding: 9px 12px; text-align: center; color: var(--text);
    border-bottom: 1px solid var(--border); font-variant-numeric: tabular-nums;
}
table.tp-table tbody tr:nth-child(even) td { background: ${row_alt}; }
table.tp-table tbody tr:hover td { background: ${row_hover}; }
table.tp-table tbody tr:last-child td { border-bottom: none; }
table.tp-table tbody td:first-child, table.tp-table thead th:first-child { text-align: left; }
table.tp-table tbody td.na { color: var(--muted); }

.tbl-caption { font-size: 0.76rem; color: var(--muted); margin: 8px 2px 4px; }

/* ---------------- Widgets Streamlit ---------------- */
.stButton > button, .stDownloadButton > button {
    width: 100%;
    background: linear-gradient(135deg, var(--primary), var(--primary-strong));
    color: #ffffff !important; border: 1px solid transparent; border-radius: 12px;
    font-weight: 600; font-size: 0.84rem; padding: 0.5rem 0.9rem;
    box-shadow: 0 12px 26px -18px var(--primary);
    transition: transform 0.18s ease, filter 0.18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-1px); filter: brightness(1.08); }

[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stTextInput input, .stNumberInput input, .stDateInput input {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}
[data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] { background: var(--surface) !important; }
[data-baseweb="menu"] li { color: var(--text) !important; }

[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
    color: var(--muted) !important; font-size: 0.82rem; font-weight: 500;
}
[data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p { color: var(--text) !important; }

[data-testid="stExpander"] {
    border: 1px solid var(--border) !important; border-radius: 14px !important;
    background: var(--surface); overflow: hidden;
}
[data-testid="stExpander"] summary { color: var(--text); font-weight: 600; }
[data-testid="stExpander"] summary:hover { color: var(--primary); }

.stTabs [data-baseweb="tab-list"] { gap: 0.35rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    height: 42px; padding: 0 15px; border-radius: 12px 12px 0 0;
    color: var(--muted); font-weight: 600; font-size: 0.85rem;
}
.stTabs [aria-selected="true"] { color: var(--text) !important; background: var(--surface); }
.stTabs [data-baseweb="tab-highlight"] { background: var(--primary); }

[data-testid="stAlert"] { border-radius: 12px; border: 1px solid var(--border); }
[data-testid="stFileUploaderDropzone"] {
    background: var(--surface); border: 1px dashed var(--border); border-radius: 14px;
}
[data-testid="stSlider"] [role="slider"] { background: var(--primary); }
[data-testid="stMetricValue"] { color: var(--text); }

/* ---------------- Divers ---------------- */
.small { font-size: 0.78rem; color: var(--muted); }
.foot {
    text-align: center; color: var(--muted); font-size: 0.78rem;
    padding: 18px 0 4px; border-top: 1px solid var(--border); margin-top: 28px;
}
hr { border-color: var(--border); }

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: ${scroll}; border-radius: 8px; }
::-webkit-scrollbar-track { background: transparent; }

@keyframes rise {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
    .hero { padding: 20px; }
    .hero-title { font-size: 1.5rem; }
    .section-head h2 { font-size: 1.18rem; }
}
</style>
"""

# -----------------------------------------------------------------------------
# Sélection du thème (lue avant l'injection CSS)
# -----------------------------------------------------------------------------
THEME_OPTIONS = ["🌙 Sombre", "☀️ Clair"]
if "theme_radio" not in st.session_state:
    st.session_state["theme_radio"] = THEME_OPTIONS[0]

MODE = "dark" if "Sombre" in st.session_state["theme_radio"] else "light"
THEME = THEMES[MODE]

st.markdown(
    Template(CSS_TEMPLATE).substitute(**THEME["css"]),
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Helpers d'interface
# -----------------------------------------------------------------------------
TYPE_META = {
    "qualitative_nominale": ("Qualitative nominale", "badge-blue", "🏷️"),
    "qualitative_ordinale": ("Qualitative ordinale", "badge-violet", "📈"),
    "quantitative_discrete": ("Quantitative discrète", "badge-green", "🔢"),
    "quantitative_continue": ("Quantitative continue", "badge-amber", "📏"),
    "inconnu": ("Type inconnu", "badge-gray", "❓"),
}

TYPE_CHOICES = [
    "qualitative_nominale",
    "qualitative_ordinale",
    "quantitative_discrete",
    "quantitative_continue",
]


def md(content: str) -> None:
    """Raccourci pour injecter du HTML."""
    st.markdown(content, unsafe_allow_html=True)


def esc(value) -> str:
    return _html.escape(str(value))


def badge_html(type_key: str) -> str:
    label, css, icon = TYPE_META.get(type_key, TYPE_META["inconnu"])
    return f'<span class="badge {css}">{icon} {esc(label)}</span>'


def fmt_num(value, decimals: int = 2) -> str:
    """Formate un nombre pour l'affichage (jamais d'exception)."""
    if value is None:
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return esc(value)
    if not np.isfinite(number):
        return "—"
    return f"{number:,.{decimals}f}".replace(",", " ")


def _fmt_float(value) -> str:
    """Formatage compact utilisé par les tableaux HTML."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not np.isfinite(number):
        return "—"
    if number == 0:
        return "0"
    absolute = abs(number)
    if absolute >= 1000:
        return f"{number:,.2f}".replace(",", " ")
    if absolute >= 10:
        return f"{number:.3f}".rstrip("0").rstrip(".")
    if absolute >= 1:
        return f"{number:.4f}".rstrip("0").rstrip(".")
    return f"{number:.5f}".rstrip("0").rstrip(".")


def show_table(data, caption: str = "", max_height: int = 460) -> None:
    """Affiche un DataFrame en tableau HTML thémé (aucun canvas)."""
    frame = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    if caption:
        md(f'<div class="tbl-caption">{esc(caption)}</div>')
    if frame.empty:
        md(callout("Tableau vide", "Aucune donnée à afficher.", "warn", "⚠️"))
        return
    html_table = frame.to_html(
        index=False,
        escape=True,
        border=0,
        classes="tp-table",
        na_rep="—",
        float_format=_fmt_float,
    )
    md(f'<div class="tbl-wrap" style="max-height:{int(max_height)}px">{html_table}</div>')


def download_csv(frame: pd.DataFrame, filename: str, label: str, key: str) -> None:
    st.download_button(
        label,
        frame.to_csv(index=False).encode("utf-8-sig"),
        filename,
        "text/csv",
        key=key,
    )


def callout(title: str, body_html: str, kind: str = "info", icon: str = "ℹ️") -> str:
    return (
        f'<div class="callout {kind}">'
        f'<div class="co-ico">{icon}</div>'
        f'<div><div class="co-title">{esc(title)}</div>'
        f'<div class="co-body">{body_html}</div></div></div>'
    )


def section_head(icon: str, title: str, subtitle: str = "") -> str:
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    return (
        f'<div class="section-head"><div class="section-ico">{icon}</div>'
        f"<div><h2>{esc(title)}</h2>{sub}</div></div>"
    )


def kpi_html(label: str, value: str, sub: str = "") -> str:
    return (
        f'<div class="kpi"><div class="kpi-label">{esc(label)}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{esc(sub)}</div></div>'
    )


def kpi_row(items) -> None:
    """items = [(label, value, sub), ...] — affichés sur une ligne de colonnes."""
    columns = st.columns(len(items))
    for column, (label, value, sub) in zip(columns, items):
        with column:
            md(kpi_html(label, value, sub))


def style_fig(fig, height: int = 400, title: str | None = None, showlegend=None):
    """Applique le thème courant à une figure Plotly."""
    chart = THEME["chart"]
    if title is not None:
        fig.update_layout(
            title=dict(text=title, x=0.01, xanchor="left",
                       font=dict(size=14, color=chart["title"]))
        )
    elif fig.layout.title.text:
        fig.update_layout(
            title=dict(text=fig.layout.title.text, x=0.01, xanchor="left",
                       font=dict(size=14, color=chart["title"]))
        )

    fig.update_layout(
        template=None,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, Segoe UI, sans-serif", size=12, color=chart["font"]),
        colorway=chart["colorway"],
        margin=dict(l=54, r=26, t=56, b=48),
        hoverlabel=dict(
            bgcolor=chart["hover_bg"],
            bordercolor=THEME["css"]["border"],
            font=dict(color=THEME["css"]["text"], family="Outfit, sans-serif"),
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=chart["font"])),
    )
    fig.update_xaxes(
        gridcolor=chart["grid"], zerolinecolor=chart["grid"],
        linecolor=THEME["css"]["border"], tickfont=dict(color=chart["font"]),
        title_font=dict(color=chart["font"]),
    )
    fig.update_yaxes(
        gridcolor=chart["grid"], zerolinecolor=chart["grid"],
        linecolor=THEME["css"]["border"], tickfont=dict(color=chart["font"]),
        title_font=dict(color=chart["font"]),
    )
    if showlegend is not None:
        fig.update_layout(showlegend=showlegend)
    return fig


def plot(fig, height: int = 400, title: str | None = None, showlegend=None) -> None:
    style_fig(fig, height=height, title=title, showlegend=showlegend)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def callout_num(series: pd.Series, message: str = "Sélectionnez une variable quantitative.") -> bool:
    """Vérifie qu'une série permet un traitement numérique."""
    if not np.issubdtype(series.dtype, np.number):
        md(callout("Variable non numérique", message, "warn", "⚠️"))
        return False
    if len(series.dropna()) < 3:
        md(callout("Effectif insuffisant",
                   "Au moins 3 valeurs sont nécessaires pour cette analyse.", "warn", "⚠️"))
        return False
    return True


# -----------------------------------------------------------------------------
# 1. Jeu de données de démonstration (Listing 2)
# -----------------------------------------------------------------------------
@st.cache_data
def get_demo_dataset() -> pd.DataFrame:
    """Jeu de données officiel de la fiche TP (50 étudiants, 6 variables)."""
    data = {
        "ID": list(range(1, 51)),
        "Genre": ["M", "F", "M", "F", "M", "F", "M", "F", "M", "F"] * 5,
        "Niveau_Etude": [
            "Licence", "Master", "Doctorat", "Licence", "Master",
            "Licence", "Master", "Doctorat", "Licence", "Master",
        ] * 5,
        "Age": [20, 22, 25, 21, 23, 26, 24, 27, 20, 22] * 5,
        "Note_Stats": [12.5, 15.0, 9.5, 17.0, 11.0, 14.5, 13.0, 16.5, 10.5, 18.0] * 5,
        "Heures_Travail": [10, 15, 8, 20, 12, 18, 14, 16, 9, 22] * 5,
    }
    return pd.DataFrame(data)


def read_uploaded(file) -> pd.DataFrame | None:
    """Lit un fichier CSV / Excel uploadé, avec détection du séparateur."""
    if file is None:
        return None
    name = file.name.lower()
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)

    last_error = None
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            file.seek(0)
            return pd.read_csv(file, sep=None, engine="python", encoding=encoding)
        except Exception as exc:  # noqa: BLE001 - on tente l'encodage suivant
            last_error = exc
    try:
        file.seek(0)
        return pd.read_csv(file)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(str(last_error or exc)) from exc


# -----------------------------------------------------------------------------
# 2. Fonctions métier de la fiche TP
# -----------------------------------------------------------------------------
def detecter_type_variable(serie: pd.Series) -> str:
    """Classification statistique automatique (Listing 3 de la fiche TP)."""
    serie_clean = serie.dropna()
    if len(serie_clean) == 0:
        return "inconnu"

    dtype = serie.dtype
    n_unique = serie_clean.nunique()

    if dtype in ["object", "category", "bool"] or (
        not np.issubdtype(dtype, np.number) and n_unique < 10
    ):
        categories = serie_clean.unique()
        mots_ordinaux = [
            "niveau", "faible", "moyen", "eleve", "licence",
            "master", "doctorat", "primaire", "secondaire",
        ]
        ordre_possible = any(mot in str(categories).lower() for mot in mots_ordinaux)
        return "qualitative_ordinale" if ordre_possible else "qualitative_nominale"

    if np.issubdtype(dtype, np.number):
        try:
            valeurs_entieres = bool(
                np.all(np.isfinite(serie_clean))
                and np.all(serie_clean == serie_clean.astype(int))
            )
        except (TypeError, ValueError):
            valeurs_entieres = False
        if valeurs_entieres and n_unique <= 20:
            return "quantitative_discrete"
        return "quantitative_continue"

    return "inconnu"


def tableau_qualitatif(df: pd.DataFrame, colonne: str) -> pd.DataFrame:
    """Tableau statistique d'une variable qualitative (Listing 4)."""
    serie = df[colonne].dropna()
    effectifs = serie.value_counts().sort_index()
    frequences = serie.value_counts(normalize=True).sort_index()

    tableau = pd.DataFrame({
        "Modalité": effectifs.index,
        "Effectif (n_i)": effectifs.values,
        "Fréquence (f_i)": np.round(frequences.values, 4),
        "Fréquence (%)": np.round(frequences.values * 100, 2),
    })
    tableau["Fréquence cumulée"] = np.round(np.cumsum(tableau["Fréquence (f_i)"].values), 4)
    tableau["Fréquence cumulée (%)"] = np.round(tableau["Fréquence cumulée"] * 100, 2)
    return tableau


def tableau_quantitatif_discret(df: pd.DataFrame, colonne: str) -> pd.DataFrame:
    """Tableau statistique d'une variable quantitative discrète (Listing 5)."""
    serie = df[colonne].dropna()
    effectifs = serie.value_counts().sort_index()
    frequences = serie.value_counts(normalize=True).sort_index()

    cumul = np.cumsum(frequences.values)
    return pd.DataFrame({
        "Valeur (x_i)": effectifs.index,
        "Effectif (n_i)": effectifs.values,
        "Fréquence (f_i)": np.round(frequences.values, 4),
        "Fréquence (%)": np.round(frequences.values * 100, 2),
        "Fréquence cumulée": np.round(cumul, 4),
        "Fréquence cumulée (%)": np.round(cumul * 100, 2),
    })


def creer_classes_sturges(serie: pd.Series):
    """Règle de Sturges : k = 1 + 3.322 · log10(n)."""
    serie = pd.Series(serie).dropna()
    n = len(serie)
    if n == 0:
        return [0.0, 1.0], 1
    minimum, maximum = float(serie.min()), float(serie.max())
    if maximum == minimum:
        return [minimum, minimum + 1.0], 1
    nb_classes = max(1, int(np.ceil(1 + 3.322 * np.log10(n))))
    amplitude = (maximum - minimum) / nb_classes
    bornes = [minimum + i * amplitude for i in range(nb_classes + 1)]
    bornes[-1] = maximum
    return bornes, nb_classes


def creer_classes_yule(serie: pd.Series):
    """Règle de Yule : k = 2.5 · n^(1/4)."""
    serie = pd.Series(serie).dropna()
    n = len(serie)
    if n == 0:
        return [0.0, 1.0], 1
    minimum, maximum = float(serie.min()), float(serie.max())
    if maximum == minimum:
        return [minimum, minimum + 1.0], 1
    nb_classes = max(1, int(np.ceil(2.5 * (n ** 0.25))))
    amplitude = (maximum - minimum) / nb_classes
    bornes = [minimum + i * amplitude for i in range(nb_classes + 1)]
    bornes[-1] = maximum
    return bornes, nb_classes


def creer_classes_freedman_diaconis(serie: pd.Series):
    """Règle de Freedman-Diaconis : h = 2 · IQR / n^(1/3)."""
    serie = pd.Series(serie).dropna()
    n = len(serie)
    if n == 0:
        return [0.0, 1.0], 1
    minimum, maximum = float(serie.min()), float(serie.max())
    if maximum == minimum:
        return [minimum, minimum + 1.0], 1
    q25, q75 = np.percentile(serie, [25, 75])
    iqr = q75 - q25
    h = 2 * iqr / (n ** (1 / 3)) if n > 0 else 0
    if h == 0 or np.isnan(h):
        h = (maximum - minimum) / 10
    nb_classes = max(1, int(np.ceil((maximum - minimum) / h)))
    bornes = [minimum + i * h for i in range(nb_classes + 1)]
    bornes[-1] = maximum
    return bornes, nb_classes


def _bornes(serie: pd.Series, methode: str = "sturges"):
    """Bornes de classes selon la règle demandée."""
    if methode == "yule":
        return creer_classes_yule(serie)[0]
    if methode == "fd":
        return creer_classes_freedman_diaconis(serie)[0]
    return creer_classes_sturges(serie)[0]


def tableau_quantitatif_continu(df: pd.DataFrame, colonne: str,
                                methode: str = "sturges") -> pd.DataFrame:
    """Tableau de fréquences d'une variable continue (Listing 6)."""
    serie = df[colonne].dropna()
    bornes = _bornes(serie, methode)

    effectifs, _ = np.histogram(serie, bins=bornes)
    frequences = effectifs / len(serie) if len(serie) else effectifs
    frequences_cumulees = np.cumsum(frequences)
    labels = [f"[{bornes[i]:.2f} ; {bornes[i + 1]:.2f}]" for i in range(len(bornes) - 1)]

    return pd.DataFrame({
        "Classe": labels,
        "Borne Inf (L_i)": [round(bornes[i], 2) for i in range(len(bornes) - 1)],
        "Borne Sup (L_i+1)": [round(bornes[i + 1], 2) for i in range(len(bornes) - 1)],
        "Amplitude (a_i)": [round(bornes[i + 1] - bornes[i], 2) for i in range(len(bornes) - 1)],
        "Effectif (n_i)": effectifs,
        "Effectif Cumulé (N_i)": np.cumsum(effectifs),
        "Fréquence (f_i)": np.round(frequences, 4),
        "Fréquence (%)": np.round(frequences * 100, 2),
        "Fréquence cumulée": np.round(frequences_cumulees, 4),
        "Fréquence cumulée (%)": np.round(frequences_cumulees * 100, 2),
    })


def parametres_position(serie: pd.Series) -> dict:
    """Paramètres de position (Listing 7)."""
    serie = pd.Series(serie).dropna()
    if len(serie) == 0:
        return {}
    mode_values = serie.mode()
    mode_result = mode_values.iloc[0] if len(mode_values) > 0 else np.nan
    return {
        "Effectif (n)": len(serie),
        "Moyenne": serie.mean(),
        "Médiane (Q2)": serie.median(),
        "Mode": mode_result,
        "Minimum": serie.min(),
        "Maximum": serie.max(),
        "Q1 (25%)": np.percentile(serie, 25),
        "Q3 (75%)": np.percentile(serie, 75),
        "D6 (60%)": np.percentile(serie, 60),
    }


def parametres_dispersion(serie: pd.Series) -> dict:
    """Paramètres de dispersion et de forme (Listing 7)."""
    serie = pd.Series(serie).dropna()
    if len(serie) == 0:
        return {}
    q1, q3 = np.percentile(serie, [25, 75])
    ecart_type = serie.std(ddof=1) if len(serie) > 1 else 0.0
    moyenne = serie.mean()
    cv = (ecart_type / moyenne * 100) if moyenne != 0 else np.nan
    return {
        "Étendue": serie.max() - serie.min(),
        "IQR (Q3 - Q1)": q3 - q1,
        "Variance (s²)": serie.var(ddof=1) if len(serie) > 1 else 0.0,
        "Écart-type (s)": ecart_type,
        "CV (%)": round(cv, 2) if not np.isnan(cv) else np.nan,
        "Asymétrie (Skewness)": serie.skew() if len(serie) > 2 else np.nan,
        "Aplatissement (Kurtosis)": serie.kurtosis() if len(serie) > 3 else np.nan,
    }


def quantile_interpole(serie: pd.Series, p: float, methode: str = "sturges") -> float:
    """Quantile Q_p par interpolation linéaire dans la classe contenant le rang p·n."""
    serie = pd.Series(serie).dropna()
    if len(serie) == 0:
        return np.nan
    bornes = _bornes(serie, methode)
    effectifs, _ = np.histogram(serie, bins=bornes)
    cumul = np.cumsum(effectifs)
    n = len(serie)
    cible = p * n

    i = int(np.searchsorted(cumul, cible, side="left"))
    i = min(max(i, 0), len(effectifs) - 1)
    avant = 0.0 if i == 0 else float(cumul[i - 1])
    ni = float(effectifs[i])
    amplitude = float(bornes[i + 1] - bornes[i])
    if ni == 0:
        return float(bornes[i])
    return float(bornes[i] + ((cible - avant) / ni) * amplitude)


def quantiles_par_interpolation(serie: pd.Series, methode: str = "sturges") -> dict:
    """Détermine Q1, Me, D6, Q3 par interpolation, avec le détail de calcul (Listing 10)."""
    serie = pd.Series(serie).dropna()
    n = len(serie)
    bornes = _bornes(serie, methode)

    effectifs, _ = np.histogram(serie, bins=bornes)
    effectifs_cum = np.cumsum(effectifs)
    amplitudes = np.diff(bornes)

    def interpoler(p):
        cible = p * n
        i = int(np.searchsorted(effectifs_cum, cible, side="left"))
        i = min(max(i, 0), len(effectifs) - 1)
        avant = 0 if i == 0 else effectifs_cum[i - 1]
        l_i = bornes[i]
        n_i = effectifs[i]
        a_i = amplitudes[i]
        valeur = l_i + ((cible - avant) / n_i) * a_i if n_i > 0 else l_i
        return float(valeur), i, float(l_i), float(avant), float(n_i), float(a_i)

    q1 = interpoler(0.25)
    me = interpoler(0.50)
    d6 = interpoler(0.60)
    q3 = interpoler(0.75)

    return {
        "Q1": q1[0],
        "Me (Q2)": me[0],
        "D6": d6[0],
        "Q3": q3[0],
        "IQR (Q3 - Q1)": q3[0] - q1[0],
        "bornes": bornes,
        "effectifs": effectifs,
        "effectifs_cum": effectifs_cum,
        "amplitudes": amplitudes,
        "details": {
            "Q1": {"idx": q1[1], "L_i": q1[2], "N_avant": q1[3], "n_i": q1[4], "a_i": q1[5], "p": 0.25},
            "Me": {"idx": me[1], "L_i": me[2], "N_avant": me[3], "n_i": me[4], "a_i": me[5], "p": 0.50},
            "D6": {"idx": d6[1], "L_i": d6[2], "N_avant": d6[3], "n_i": d6[4], "a_i": d6[5], "p": 0.60},
            "Q3": {"idx": q3[1], "L_i": q3[2], "N_avant": q3[3], "n_i": q3[4], "a_i": q3[5], "p": 0.75},
        },
    }


def courbe_cumulative_quantiles(serie: pd.Series, methode: str = "sturges"):
    """Courbe cumulative et quantiles interpolés (Listing 12)."""
    serie = pd.Series(serie).dropna()
    n = len(serie)
    bornes = _bornes(serie, methode)

    effectifs, _ = np.histogram(serie, bins=bornes)
    f_cum = np.cumsum(effectifs) / n if n else np.zeros(len(effectifs))
    amplitudes = np.diff(bornes)

    def interpoler(p):
        i = int(np.searchsorted(f_cum, p, side="left"))
        i = min(max(i, 0), len(effectifs) - 1)
        avant = 0.0 if i == 0 else float(f_cum[i - 1])
        l_i = float(bornes[i])
        f_i = float(effectifs[i]) / n if n else 0.0
        a_i = float(amplitudes[i])
        return l_i + ((p - avant) / f_i) * a_i if f_i > 0 else l_i

    quantiles = {
        "Q1 (25%)": interpoler(0.25),
        "Q2 - Médiane (50%)": interpoler(0.50),
        "D6 (60%)": interpoler(0.60),
        "Q3 (75%)": interpoler(0.75),
    }
    return bornes, f_cum, quantiles


def parametres_tukey(serie: pd.Series) -> dict:
    """Les cinq paramètres du diagramme de Tukey (Listings 16)."""
    serie = pd.Series(serie).dropna()
    q1 = float(np.percentile(serie, 25))
    q2 = float(np.percentile(serie, 50))
    q3 = float(np.percentile(serie, 75))
    iqr = q3 - q1
    return {
        "Q1": q1,
        "Q2 (Médiane)": q2,
        "Q3": q3,
        "IQR": iqr,
        "L_inf (Modéré)": q1 - 1.5 * iqr,
        "L_sup (Modéré)": q3 + 1.5 * iqr,
        "L_inf_ext (Extrême)": q1 - 3.0 * iqr,
        "L_sup_ext (Extrême)": q3 + 3.0 * iqr,
        "Min": float(serie.min()),
        "Max": float(serie.max()),
        "Moyenne": float(serie.mean()),
        "Écart-type": float(serie.std(ddof=1)) if len(serie) > 1 else 0.0,
    }


def z_scores(serie: pd.Series) -> pd.Series:
    """Z-scores (ddof = 0, comme scipy.stats.zscore)."""
    serie = pd.Series(serie).dropna()
    ecart = serie.std(ddof=0)
    if not np.isfinite(ecart) or ecart == 0:
        return pd.Series(0.0, index=serie.index)
    return (serie - serie.mean()) / ecart


def detecter_points_aberrants(df: pd.DataFrame, colonne: str) -> pd.DataFrame:
    """Points aberrants selon le critère de Tukey (Listing 17)."""
    serie = df[colonne].dropna()
    if len(serie) < 4:
        return pd.DataFrame(columns=["Index", "Valeur", "Type", "Écart à la médiane", "Z-Score"])

    params = parametres_tukey(serie)
    outliers = serie[
        (serie < params["L_inf (Modéré)"]) | (serie > params["L_sup (Modéré)"])
    ]
    if len(outliers) == 0:
        return pd.DataFrame(columns=["Index", "Valeur", "Type", "Écart à la médiane", "Z-Score"])

    z_map = z_scores(serie).to_dict()
    types = []
    for value in outliers.values:
        if value < params["L_inf_ext (Extrême)"] or value > params["L_sup_ext (Extrême)"]:
            types.append("Extrême (> 3×IQR)")
        else:
            types.append("Modéré (1.5×IQR – 3×IQR)")

    return pd.DataFrame({
        "Index": outliers.index,
        "Valeur": outliers.values,
        "Type": types,
        "Écart à la médiane": np.round(outliers.values - params["Q2 (Médiane)"], 4),
        "Z-Score": [round(z_map[i], 3) for i in outliers.index],
    })


def parametres_table(serie: pd.Series) -> pd.DataFrame:
    """Tableau récapitulatif position + dispersion."""
    rows = []
    for label, value in parametres_position(serie).items():
        rows.append({"Famille": "Position", "Paramètre": label, "Valeur": value})
    for label, value in parametres_dispersion(serie).items():
        rows.append({"Famille": "Dispersion / forme", "Paramètre": label, "Valeur": value})
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Barre latérale
# -----------------------------------------------------------------------------
NAV = {
    1: ("Vue globale", "🔍"),
    2: ("Tableaux & graphiques", "📊"),
    3: ("Position & dispersion", "📐"),
    4: ("Interpolation", "⚖️"),
    5: ("Courbe cumulative", "📈"),
    6: ("Tukey & outliers", "📦"),
    7: ("Discrétisation", "🔄"),
    8: ("Opération inverse", "↩️"),
    9: ("Synthèse", "🧾"),
    10: ("Exercices", "🧪"),
}

SRC_DEMO = "Jeu de démonstration (TP)"
SRC_FILE = "Importer un fichier"

with st.sidebar:
    md(
        '<div class="brand">'
        '<div class="brand-logo">📊</div>'
        '<div><div class="brand-name">AutoSTAT</div>'
        '<div class="brand-sub">Statistique descriptive · 2025–2026</div></div>'
        "</div>"
    )

    md('<div class="side-title">Apparence</div>')
    st.radio(
        "Apparence",
        THEME_OPTIONS,
        key="theme_radio",
        label_visibility="collapsed",
    )

    md('<div class="divider"></div>')
    md('<div class="side-title">Source des données</div>')
    source_choisie = st.radio(
        "Source",
        [SRC_DEMO, SRC_FILE],
        key="source_radio",
        label_visibility="collapsed",
    )

    df_actuel: pd.DataFrame | None = None
    nom_source = ""

    if source_choisie == SRC_DEMO:
        df_actuel = get_demo_dataset()
        nom_source = "Dataset démo · 50 étudiants"
        st.success("50 lignes · 6 colonnes")
    else:
        fichier = st.file_uploader(
            "Fichier CSV ou Excel",
            type=["csv", "xlsx", "xls"],
            key="uploader",
        )
        if fichier is not None:
            try:
                df_actuel = read_uploaded(fichier)
                if df_actuel is None or df_actuel.empty:
                    raise ValueError("le fichier ne contient aucune ligne")
                nom_source = fichier.name
                st.success(f"{df_actuel.shape[0]} lignes · {df_actuel.shape[1]} colonnes")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Lecture impossible : {exc}")
                df_actuel = get_demo_dataset()
                nom_source = "Dataset démo (secours)"
        else:
            st.info("Aucun fichier importé — dataset démo utilisé.")
            df_actuel = get_demo_dataset()
            nom_source = "Dataset démo · en attente d'import"

    md('<div class="divider"></div>')
    md('<div class="side-title">Variable d’étude</div>')

    colonnes_dispos = [c for c in df_actuel.columns if str(c).upper() != "ID"]
    if not colonnes_dispos:
        colonnes_dispos = list(df_actuel.columns)

    index_defaut = (
        colonnes_dispos.index("Note_Stats") if "Note_Stats" in colonnes_dispos else 0
    )
    colonne_selectionnee = st.selectbox(
        "Colonne analysée",
        colonnes_dispos,
        index=index_defaut,
    )

    type_auto = detecter_type_variable(df_actuel[colonne_selectionnee])
    type_effectif = type_auto

    md(f'<div style="margin:2px 0 10px;">{badge_html(type_auto)}</div>')

    with st.expander("⚙️ Forcer le type détecté"):
        forcer_type = st.checkbox("Modifier manuellement", key="forcer_type")
        if forcer_type:
            type_effectif = st.selectbox(
                "Type retenu",
                TYPE_CHOICES,
                index=TYPE_CHOICES.index(type_auto) if type_auto in TYPE_CHOICES else 0,
                key="type_force",
            )

    md('<div class="divider"></div>')
    md('<div class="side-title">Navigation</div>')
    section = st.radio(
        "Navigation",
        list(NAV.keys()),
        format_func=lambda n: f"{n:02d} · {NAV[n][1]}",
        key="nav_section",
        label_visibility="collapsed",
    )

    md('<div class="divider"></div>')
    md(
        '<div class="small" style="line-height:1.6;">'
        "TP Statistique descriptive — 6 h<br>"
        "Pandas · NumPy · Plotly · Streamlit<br>"
        "<span style='opacity:.8;'>Thème clair / sombre intégré</span>"
        "</div>"
    )

label_t, class_t, icon_t = TYPE_META.get(type_effectif, TYPE_META["inconnu"])

# -----------------------------------------------------------------------------
# En-tête
# -----------------------------------------------------------------------------
md(
    f"""
<div class="hero">
    <div class="hero-top">
        <div>
            <div class="hero-eyebrow">Fiche TP · Statistique descriptive</div>
            <h1 class="hero-title">Dashboard statistique interactif</h1>
            <p class="hero-sub">
                Détection automatique des types, tableaux et graphiques, paramètres,
                interpolation linéaire, courbe cumulative, diagramme de Tukey et discrétisation.
            </p>
        </div>
        <div>{badge_html(type_effectif)}</div>
    </div>
    <div class="hero-chips">
        <span class="chip">📁 {esc(nom_source)}</span>
        <span class="chip">👥 n = {len(df_actuel)}</span>
        <span class="chip">🧮 {len(df_actuel.columns)} variables</span>
        <span class="chip">🎯 {esc(colonne_selectionnee)}</span>
    </div>
</div>
"""
)

# -----------------------------------------------------------------------------
# SECTION 1 — Vue globale & détection des types
# -----------------------------------------------------------------------------
if section == 1:
    md(section_head("🔍", "Vue globale & détection des types",
                    "Aperçu du jeu de données et classification statistique de chaque colonne."))

    left, right = st.columns(2, gap="large")
    with left:
        md(callout(
            "Variables qualitatives",
            "<b>Nominale</b> — catégories sans hiérarchie (ex. <i>Genre</i>).<br>"
            "<b>Ordinale</b> — catégories ordonnées (ex. <i>Niveau d’étude</i>).",
            "info", "🏷️",
        ))
    with right:
        md(callout(
            "Variables quantitatives",
            "<b>Discrète</b> — entiers, peu de valeurs distinctes (ex. <i>Âge</i>).<br>"
            "<b>Continue</b> — mesures réelles (ex. <i>Note_Stats</i>).",
            "info", "📏",
        ))

    summary_rows = []
    for colonne in df_actuel.columns:
        serie_col = df_actuel[colonne]
        detected = detecter_type_variable(serie_col)
        label, _css, icon = TYPE_META.get(detected, TYPE_META["inconnu"])
        exemples = serie_col.dropna().unique()[:4].tolist()
        summary_rows.append({
            "Colonne": colonne,
            "Type détecté": f"{icon} {label}",
            "dtype": str(serie_col.dtype),
            "Valeurs uniques": serie_col.nunique(),
            "Manquants": int(serie_col.isna().sum()),
            "Exemples": ", ".join(str(v) for v in exemples),
        })
    df_summary = pd.DataFrame(summary_rows)

    nb_quant = sum(1 for row in summary_rows if "Quantitative" in row["Type détecté"])
    nb_qual = sum(1 for row in summary_rows if "Qualitative" in row["Type détecté"])

    kpi_row([
        ("Taille de l’échantillon", f"{len(df_actuel)}", "lignes observées"),
        ("Variables", f"{len(df_actuel.columns)}", "colonnes du dataset"),
        ("Quantitatives", f"{nb_quant}", "discrètes ou continues"),
        ("Qualitatives", f"{nb_qual}", "nominales ou ordinales"),
    ])

    st.write("")
    md('<div class="mini-title">Classification des variables</div>')
    show_table(df_summary, max_height=420)

    with st.expander("👀 Explorer les données brutes (15 premières lignes)", expanded=True):
        show_table(df_actuel.head(15), max_height=380)

# -----------------------------------------------------------------------------
# SECTION 2 — Tableaux & graphiques
# -----------------------------------------------------------------------------
elif section == 2:
    md(section_head("📊", f"Tableaux & graphiques — {colonne_selectionnee}",
                    "Représentations adaptées au type statistique de la variable."))

    serie_select = df_actuel[colonne_selectionnee]

    # ---------- Variable qualitative ----------
    if "qualitative" in type_effectif:
        md(callout(
            "Variable qualitative",
            f"Tableau des effectifs et des fréquences, diagramme en tuyaux d’orgues "
            f"et diagramme circulaire pour <b>{esc(colonne_selectionnee)}</b>.",
            "info", "🏷️",
        ))
        tab_stat = tableau_qualitatif(df_actuel, colonne_selectionnee)

        left, right = st.columns([1.15, 1.35], gap="large")
        with left:
            md('<div class="mini-title">Tableau statistique</div>')
            show_table(tab_stat, max_height=360)
            download_csv(tab_stat, f"tableau_{colonne_selectionnee}.csv",
                         "📥 Exporter le tableau (CSV)", key="dl_qual")

        with right:
            fig_pie = px.pie(
                tab_stat,
                names="Modalité",
                values="Effectif (n_i)",
                hole=0.42,
                color_discrete_sequence=THEME["chart"]["colorway"],
            )
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent+label",
                marker=dict(line=dict(color=THEME["chart"]["pie_line"], width=2)),
            )
            plot(fig_pie, height=360, title=f"Répartition de {colonne_selectionnee}")

        st.write("")
        md('<div class="mini-title">Diagramme en tuyaux d’orgues</div>')
        fig_bar = px.bar(
            tab_stat,
            x="Modalité",
            y="Effectif (n_i)",
            text="Effectif (n_i)",
            color="Modalité",
            color_discrete_sequence=THEME["chart"]["colorway"],
        )
        fig_bar.update_traces(
            texttemplate="%{text}",
            textposition="outside",
            marker_line_color=THEME["css"]["border"],
            marker_line_width=1.5,
        )
        fig_bar.update_layout(showlegend=False)
        plot(fig_bar, height=380, title=f"Effectifs par modalité — {colonne_selectionnee}")

    # ---------- Variable quantitative discrète ----------
    elif type_effectif == "quantitative_discrete" and np.issubdtype(serie_select.dtype, np.number):
        md(callout(
            "Variable quantitative discrète",
            "Tableau des effectifs, diagramme en bâtons et courbe cumulative en escalier.",
            "info", "🔢",
        ))
        tab_disc = tableau_quantitatif_discret(df_actuel, colonne_selectionnee)

        left, right = st.columns([1.15, 1.35], gap="large")
        with left:
            md('<div class="mini-title">Tableau statistique</div>')
            show_table(tab_disc, max_height=360)
            download_csv(tab_disc, f"tableau_{colonne_selectionnee}.csv",
                         "📥 Exporter le tableau (CSV)", key="dl_disc")

        with right:
            fig_baton = go.Figure()
            for _, row in tab_disc.iterrows():
                fig_baton.add_trace(go.Scatter(
                    x=[row["Valeur (x_i)"], row["Valeur (x_i)"]],
                    y=[0, row["Effectif (n_i)"]],
                    mode="lines",
                    line=dict(color=THEME["chart"]["colorway"][2], width=5),
                    showlegend=False,
                    hoverinfo="skip",
                ))
            fig_baton.add_trace(go.Scatter(
                x=tab_disc["Valeur (x_i)"],
                y=tab_disc["Effectif (n_i)"],
                mode="markers",
                marker=dict(size=12, color=THEME["chart"]["colorway"][2],
                            line=dict(color=THEME["chart"]["pie_line"], width=2)),
                name="Effectif",
            ))
            plot(fig_baton, height=360,
                 title=f"Diagramme en bâtons — {colonne_selectionnee}", showlegend=False)

        st.write("")
        md('<div class="mini-title">Courbe cumulative en escalier</div>')
        fig_step = go.Figure()
        fig_step.add_trace(go.Scatter(
            x=tab_disc["Valeur (x_i)"],
            y=tab_disc["Fréquence cumulée"],
            mode="lines+markers",
            line_shape="hv",
            line=dict(color=THEME["chart"]["colorway"][3], width=3),
            marker=dict(size=8, color=THEME["chart"]["colorway"][3]),
            name="F(x)",
        ))
        fig_step.update_layout(yaxis=dict(range=[0, 1.05], title="Fréquence cumulée F(x)"))
        plot(fig_step, height=400, title=f"Fonction de répartition — {colonne_selectionnee}")

    # ---------- Variable quantitative continue ----------
    else:
        if not callout_num(serie_select, "Cette variable doit être numérique pour être discrétisée."):
            st.stop()

        md(callout(
            "Variable quantitative continue",
            "Comparaison des trois règles de discrétisation, histogramme et ogive.",
            "info", "📏",
        ))
        regle = st.radio(
            "Règle de discrétisation",
            [
                "sturges · k = 1 + 3.322 log10(n)",
                "yule · k = 2.5 n^(1/4)",
                "fd · h = 2·IQR / n^(1/3)",
            ],
            index=0,
            horizontal=True,
        )
        code_regle = regle.split()[0]
        nom_regle = {"sturges": "Sturges", "yule": "Yule", "fd": "Freedman–Diaconis"}[code_regle]

        tab_cont = tableau_quantitatif_continu(df_actuel, colonne_selectionnee, code_regle)
        bornes = _bornes(serie_select, code_regle)

        md('<div class="mini-title">Tableau des classes</div>')
        show_table(tab_cont, max_height=380, caption=f"Règle de {nom_regle} — {len(bornes) - 1} classes")

        left, right = st.columns(2, gap="large")
        with left:
            md('<div class="mini-title">Histogramme</div>')
            fig_hist = px.histogram(
                serie_select,
                x=serie_select.name if serie_select.name else None,
                nbins=len(bornes) - 1,
                color_discrete_sequence=[THEME["chart"]["colorway"][5]],
            )
            fig_hist.update_traces(
                xbins=dict(start=bornes[0], end=bornes[-1],
                           size=(bornes[-1] - bornes[0]) / max(len(bornes) - 1, 1)),
                marker_line_color=THEME["chart"]["pie_line"],
                marker_line_width=1.5,
            )
            fig_hist.update_layout(bargap=0.04)
            plot(fig_hist, height=360, title=f"Histogramme — {nom_regle}")

        with right:
            md('<div class="mini-title">Courbe cumulative (ogive)</div>')
            bornes_og, f_cum_og, _ = courbe_cumulative_quantiles(serie_select, code_regle)
            fig_ogive = go.Figure()
            fig_ogive.add_trace(go.Scatter(
                x=bornes_og[1:],
                y=f_cum_og,
                mode="lines+markers",
                line=dict(color=THEME["chart"]["colorway"][1], width=3),
                fill="tozeroy",
                fillcolor="rgba(6, 182, 212, 0.12)",
                marker=dict(size=8, color=THEME["chart"]["colorway"][1]),
                name="Fréquence cumulée",
            ))
            fig_ogive.update_layout(yaxis=dict(range=[0, 1.05], title="Fréquence cumulée F(x)"))
            plot(fig_ogive, height=360, title=f"Ogive — {nom_regle}", showlegend=False)

# -----------------------------------------------------------------------------
# SECTION 3 — Paramètres de position & dispersion
# -----------------------------------------------------------------------------
elif section == 3:
    md(section_head("📐", f"Position & dispersion — {colonne_selectionnee}",
                    "Paramètres numériques, table récapitulative et visualisations annotées."))

    serie = df_actuel[colonne_selectionnee].dropna()
    if not callout_num(serie):
        st.stop()

    p_pos = parametres_position(serie)
    p_disp = parametres_dispersion(serie)

    md('<div class="mini-title">Position</div>')
    kpi_row([
        ("Moyenne (x̄)", fmt_num(p_pos["Moyenne"]), "centre de gravité"),
        ("Médiane (Q2)", fmt_num(p_pos["Médiane (Q2)"]), "valeur 50 %"),
        ("Mode (Mo)", fmt_num(p_pos["Mode"]), "valeur la plus fréquente"),
        ("Q1 / Q3", f"{fmt_num(p_pos['Q1 (25%)'], 1)} / {fmt_num(p_pos['Q3 (75%)'], 1)}", "25 % et 75 %"),
    ])

    st.write("")
    md('<div class="mini-title">Dispersion & forme</div>')
    kpi_row([
        ("Étendue (E)", fmt_num(p_disp["Étendue"]), "max − min"),
        ("IQR", fmt_num(p_disp["IQR (Q3 - Q1)"]), "Q3 − Q1"),
        ("Écart-type (s)", fmt_num(p_disp["Écart-type (s)"]), f"variance = {fmt_num(p_disp['Variance (s²)'])}"),
        ("Coefficient de variation", f"{fmt_num(p_disp['CV (%)'])} %", "s / x̄ × 100"),
    ])

    st.write("")
    with st.expander("📋 Tableau récapitulatif de tous les paramètres", expanded=True):
        show_table(parametres_table(serie), max_height=460)

    tab_pos, tab_disp = st.tabs([
        "Lignes de position",
        "Zones de dispersion",
    ])

    with tab_pos:
        fig_pos = go.Figure()
        fig_pos.add_trace(go.Histogram(
            x=serie,
            name="Distribution",
            marker=dict(color="rgba(99, 102, 241, 0.55)",
                        line=dict(color=THEME["chart"]["pie_line"], width=1.2)),
            opacity=0.85,
        ))
        for value, label, color, dash in [
            (p_pos["Moyenne"], f"Moyenne = {fmt_num(p_pos['Moyenne'])}", THEME["css"]["danger"], "solid"),
            (p_pos["Médiane (Q2)"], f"Médiane = {fmt_num(p_pos['Médiane (Q2)'])}", THEME["css"]["success"], "dash"),
            (p_pos["Q1 (25%)"], f"Q1 = {fmt_num(p_pos['Q1 (25%)'])}", THEME["css"]["warning"], "dot"),
            (p_pos["Q3 (75%)"], f"Q3 = {fmt_num(p_pos['Q3 (75%)'])}", THEME["chart"]["colorway"][5], "dot"),
        ]:
            fig_pos.add_vline(x=value, line_width=2, line_dash=dash,
                              line_color=color, annotation_text=label,
                              annotation_position="top")
        plot(fig_pos, height=430, title="Paramètres de position sur l’histogramme")

    with tab_disp:
        fig_disp = go.Figure()
        fig_disp.add_trace(go.Histogram(
            x=serie,
            name="Distribution",
            marker=dict(color="rgba(16, 185, 129, 0.45)",
                        line=dict(color=THEME["chart"]["pie_line"], width=1.2)),
            opacity=0.85,
        ))
        fig_disp.add_vrect(
            x0=p_pos["Q1 (25%)"], x1=p_pos["Q3 (75%)"],
            fillcolor="rgba(59, 130, 246, 0.18)", layer="below", line_width=0,
            annotation_text=f"IQR = {fmt_num(p_disp['IQR (Q3 - Q1)'])}",
            annotation_position="top left",
        )
        x_bar = p_pos["Moyenne"]
        ecart = p_disp["Écart-type (s)"]
        fig_disp.add_vline(x=x_bar, line_width=2, line_color=THEME["css"]["danger"],
                           annotation_text="x̄", annotation_position="top")
        fig_disp.add_vline(x=x_bar - ecart, line_width=2, line_dash="dash",
                           line_color=THEME["chart"]["colorway"][5],
                           annotation_text="x̄ − s", annotation_position="bottom")
        fig_disp.add_vline(x=x_bar + ecart, line_width=2, line_dash="dash",
                           line_color=THEME["chart"]["colorway"][5],
                           annotation_text="x̄ + s", annotation_position="bottom")
        plot(fig_disp, height=430, title="Zone interquartile et intervalle [x̄ − s ; x̄ + s]")

# -----------------------------------------------------------------------------
# SECTION 4 — Interpolation linéaire
# -----------------------------------------------------------------------------
elif section == 4:
    md(section_head("⚖️", "Interpolation linéaire sur histogramme",
                    "Détermination de Q1, Me et Q3 à partir des données regroupées en classes."))

    st.markdown(
        "Lorsque les données sont regroupées en classes, on approxime le quantile "
        "$Q_p$ par interpolation linéaire à l’intérieur de la classe qui le contient :"
    )
    st.latex(r"Q_p = L_i + \left(\frac{p \cdot n - N_{i-1}}{n_i}\right) \times a_i")
    md(callout(
        "Légende",
        "$L_i$ borne inférieure de la classe · $p$ rang relatif (0.25, 0.50, 0.75) · "
        "$N_{i-1}$ effectif cumulé avant la classe · $n_i$ effectif de la classe · "
        "$a_i$ amplitude · $n$ effectif total.",
        "info", "📖",
    ))

    serie = df_actuel[colonne_selectionnee].dropna()
    if not callout_num(serie):
        st.stop()

    methode = st.selectbox("Règle de discrétisation", ["sturges", "yule", "fd"], index=0)
    res = quantiles_par_interpolation(serie, methode)

    bornes = res["bornes"]
    effectifs = res["effectifs"]
    effectifs_cum = res["effectifs_cum"]
    amplitudes = res["amplitudes"]

    rows = []
    for i in range(len(effectifs)):
        annotations = []
        for key, libelle in [("Q1", "Q1"), ("Me", "Me"), ("D6", "D6"), ("Q3", "Q3")]:
            if i == res["details"][key]["idx"]:
                annotations.append(libelle)
        rows.append({
            "Classe [L_i ; L_i+1[": f"[{bornes[i]:.2f} ; {bornes[i + 1]:.2f}[",
            "n_i": int(effectifs[i]),
            "N_i": int(effectifs_cum[i]),
            "a_i": round(float(amplitudes[i]), 2),
            "Quantile(s)": " · ".join(annotations),
        })
    show_table(pd.DataFrame(rows), max_height=380, caption="Tableau de calcul détaillé")

    st.write("")
    kpi_row([
        ("Q1 interpolé (25 %)", fmt_num(res["Q1"], 4),
         f"classe [{bornes[res['details']['Q1']['idx']]:.2f} ; {bornes[res['details']['Q1']['idx'] + 1]:.2f}["),
        ("Médiane interpolée (50 %)", fmt_num(res["Me (Q2)"], 4),
         f"classe [{bornes[res['details']['Me']['idx']]:.2f} ; {bornes[res['details']['Me']['idx'] + 1]:.2f}["),
        ("Q3 interpolé (75 %)", fmt_num(res["Q3"], 4),
         f"classe [{bornes[res['details']['Q3']['idx']]:.2f} ; {bornes[res['details']['Q3']['idx'] + 1]:.2f}["),
    ])

    st.write("")
    md('<div class="mini-title">Valeurs exactes vs valeurs interpolées</div>')
    q_exact = {
        "Q1 (25%)": np.percentile(serie, 25),
        "Médiane Me (50%)": np.percentile(serie, 50),
        "D6 (60%)": np.percentile(serie, 60),
        "Q3 (75%)": np.percentile(serie, 75),
    }
    interp = {
        "Q1 (25%)": res["Q1"],
        "Médiane Me (50%)": res["Me (Q2)"],
        "D6 (60%)": res["D6"],
        "Q3 (75%)": res["Q3"],
    }
    comp = pd.DataFrame({
        "Quantile": list(q_exact.keys()),
        "Exact": [round(v, 4) for v in q_exact.values()],
        f"Interpolé ({methode})": [round(interp[k], 4) for k in q_exact],
    })
    comp["Écart absolu"] = (comp[f"Interpolé ({methode})"] - comp["Exact"]).round(4)
    comp["Écart relatif (%)"] = (
        (comp["Écart absolu"].abs() / comp["Exact"].abs().replace(0, np.nan)) * 100
    ).round(2)
    show_table(comp, max_height=300)
    download_csv(comp, f"interpolation_{methode}.csv",
                 "📥 Exporter la comparaison (CSV)", key="dl_interp")

    fig_int = go.Figure()
    fig_int.add_trace(go.Histogram(
        x=serie,
        xbins=dict(start=bornes[0], end=bornes[-1],
                   size=float(amplitudes[0]) if len(amplitudes) else None),
        name="Effectifs",
        marker=dict(color="rgba(129, 140, 248, 0.55)",
                    line=dict(color=THEME["chart"]["pie_line"], width=1.2)),
    ))
    fig_int.add_vrect(
        x0=res["Q1"], x1=res["Q3"],
        fillcolor="rgba(99, 102, 241, 0.16)", layer="below", line_width=0,
        annotation_text=f"IQR = {fmt_num(res['IQR (Q3 - Q1)'])}",
        annotation_position="top left",
    )
    fig_int.add_vline(x=res["Q1"], line_width=2, line_dash="dash",
                      line_color=THEME["css"]["warning"],
                      annotation_text=f"Q1 = {fmt_num(res['Q1'])}")
    fig_int.add_vline(x=res["Me (Q2)"], line_width=2,
                      line_color=THEME["css"]["danger"],
                      annotation_text=f"Me = {fmt_num(res['Me (Q2)'])}")
    fig_int.add_vline(x=res["Q3"], line_width=2, line_dash="dash",
                      line_color=THEME["chart"]["colorway"][5],
                      annotation_text=f"Q3 = {fmt_num(res['Q3'])}")
    plot(fig_int, height=430, title="Quantiles déterminés par interpolation")

# -----------------------------------------------------------------------------
# SECTION 5 — Courbe cumulative & quantiles
# -----------------------------------------------------------------------------
elif section == 5:
    md(section_head("📈", "Courbe cumulative & quantiles",
                    "Lecture graphique de Q1, Me, D6 et Q3 sur l’ogive des fréquences cumulées."))

    st.markdown(
        "Pour lire un quantile $Q_p$ sur l’ogive : on trace l’horizontale à la hauteur "
        "$p$, on repère l’intersection avec la courbe, puis on projette verticalement "
        "sur l’axe des abscisses."
    )

    serie = df_actuel[colonne_selectionnee].dropna()
    if not callout_num(serie):
        st.stop()

    methode_ogive = st.selectbox("Règle de discrétisation (ogive)",
                                 ["sturges", "yule", "fd"], index=0)
    bornes, f_cum, quantiles_og = courbe_cumulative_quantiles(serie, methode_ogive)

    tab_quantiles = pd.DataFrame([
        {"Quantile": "Q1", "Fréquence cumulée": 0.25,
         "Valeur": round(quantiles_og["Q1 (25%)"], 4),
         "Interprétation": f"25 % des individus ont {colonne_selectionnee} ≤ {quantiles_og['Q1 (25%)']:.2f}"},
        {"Quantile": "Q2 = Me", "Fréquence cumulée": 0.50,
         "Valeur": round(quantiles_og["Q2 - Médiane (50%)"], 4),
         "Interprétation": f"50 % des individus ont {colonne_selectionnee} ≤ {quantiles_og['Q2 - Médiane (50%)']:.2f}"},
        {"Quantile": "D6", "Fréquence cumulée": 0.60,
         "Valeur": round(quantiles_og["D6 (60%)"], 4),
         "Interprétation": f"60 % des individus ont {colonne_selectionnee} ≤ {quantiles_og['D6 (60%)']:.2f}"},
        {"Quantile": "Q3", "Fréquence cumulée": 0.75,
         "Valeur": round(quantiles_og["Q3 (75%)"], 4),
         "Interprétation": f"75 % des individus ont {colonne_selectionnee} ≤ {quantiles_og['Q3 (75%)']:.2f}"},
    ])
    show_table(tab_quantiles, max_height=300, caption="Tableau récapitulatif des quantiles")

    fig_og = go.Figure()
    fig_og.add_trace(go.Scatter(
        x=bornes[1:], y=f_cum,
        mode="lines+markers",
        name="Courbe cumulative",
        line=dict(color=THEME["chart"]["colorway"][1], width=3),
        fill="tozeroy",
        fillcolor="rgba(6, 182, 212, 0.10)",
    ))

    cibles = {
        "Q1 (25%)": (THEME["css"]["warning"], 0.25, "Q1"),
        "Q2 - Médiane (50%)": (THEME["css"]["danger"], 0.50, "Me"),
        "D6 (60%)": (THEME["chart"]["colorway"][4], 0.60, "D6"),
        "Q3 (75%)": (THEME["chart"]["colorway"][5], 0.75, "Q3"),
    }
    for nom, (color, p_value, short) in cibles.items():
        valeur = quantiles_og[nom]
        fig_og.add_trace(go.Scatter(
            x=[bornes[0], valeur], y=[p_value, p_value],
            mode="lines", line=dict(color=color, width=1.5, dash="dash"),
            showlegend=False, hoverinfo="skip",
        ))
        fig_og.add_trace(go.Scatter(
            x=[valeur, valeur], y=[0, p_value],
            mode="lines", line=dict(color=color, width=1.5, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))
        fig_og.add_trace(go.Scatter(
            x=[valeur], y=[p_value],
            mode="markers+text",
            marker=dict(size=11, color=color,
                        line=dict(color=THEME["chart"]["pie_line"], width=2)),
            text=[f"{short} = {valeur:.2f}"],
            textposition="top left",
            name=short,
        ))

    fig_og.update_layout(yaxis=dict(range=[0, 1.05], title="Fréquence cumulée"))
    plot(fig_og, height=480, title="Lecture graphique des quantiles sur l’ogive")

    # Interprétation automatique
    moyenne = serie.mean()
    mediane = serie.median()
    quartiles = np.percentile(serie, [25, 75])
    iqr = quartiles[1] - quartiles[0]
    d6 = np.percentile(serie, 60)
    ecart_type = serie.std(ddof=1)

    if ecart_type == 0:
        symetrie = "Distribution <b>dégénérée</b> (écart-type nul)."
    elif abs(moyenne - mediane) < 0.1 * ecart_type:
        symetrie = "Distribution <b>quasi symétrique</b> (moyenne ≈ médiane)."
    elif moyenne > mediane:
        symetrie = "Distribution <b>asymétrique à droite</b> (moyenne &gt; médiane)."
    else:
        symetrie = "Distribution <b>asymétrique à gauche</b> (moyenne &lt; médiane)."

    dispersion = (
        "Données <b>concentrées</b> autour de la médiane (IQR &lt; écart-type)."
        if iqr < ecart_type
        else "Données <b>dispersées</b> dans les 50 % centraux (IQR &gt; écart-type)."
    )

    md(callout(
        "Interprétation automatique",
        f"• <b>Forme :</b> {symetrie}<br>"
        f"• <b>Dispersion centrale :</b> {dispersion} "
        f"(IQR = {fmt_num(iqr)}, s = {fmt_num(ecart_type)})<br>"
        f"• <b>Queue supérieure :</b> D6 − Me = {fmt_num(d6 - mediane)}.",
        "success", "🧠",
    ))

# -----------------------------------------------------------------------------
# SECTION 6 — Tukey & points aberrants
# -----------------------------------------------------------------------------
elif section == 6:
    md(section_head("📦", f"Diagramme de Tukey — {colonne_selectionnee}",
                    "Boîte à moustaches, bornes de Tukey et détection des points aberrants."))

    st.markdown(
        "Bornes de Tukey : $L_{inf} = Q_1 - 1{,}5 \\times IQR$ et "
        "$L_{sup} = Q_3 + 1{,}5 \\times IQR$. Les points situés hors de ces bornes "
        "sont déclarés aberrants ; ils sont *extrêmes* au-delà de $3 \\times IQR$."
    )

    serie = df_actuel[colonne_selectionnee].dropna()
    if not callout_num(serie):
        st.stop()

    p_tukey = parametres_tukey(serie)
    outliers_df = detecter_points_aberrants(df_actuel, colonne_selectionnee)

    kpi_row([
        ("Borne inférieure (L_inf)", fmt_num(p_tukey["L_inf (Modéré)"]), "Q1 − 1.5 × IQR"),
        ("Médiane (Q2)", fmt_num(p_tukey["Q2 (Médiane)"]), "ligne centrale"),
        ("Borne supérieure (L_sup)", fmt_num(p_tukey["L_sup (Modéré)"]), "Q3 + 1.5 × IQR"),
        ("Points aberrants", f"{len(outliers_df)}", "au-delà des bornes"),
    ])

    fig_tukey = go.Figure()
    fig_tukey.add_trace(go.Box(
        y=serie,
        name=colonne_selectionnee,
        boxpoints="all",
        jitter=0.35,
        pointpos=-1.7,
        marker=dict(color=THEME["chart"]["colorway"][1], size=6),
        line=dict(color=THEME["chart"]["colorway"][0], width=2),
        fillcolor="rgba(99, 102, 241, 0.25)",
    ))
    fig_tukey.add_hline(y=p_tukey["L_inf (Modéré)"], line_dash="dash",
                        line_color=THEME["css"]["warning"],
                        annotation_text=f"L_inf = {fmt_num(p_tukey['L_inf (Modéré)'])}")
    fig_tukey.add_hline(y=p_tukey["L_sup (Modéré)"], line_dash="dash",
                        line_color=THEME["css"]["warning"],
                        annotation_text=f"L_sup = {fmt_num(p_tukey['L_sup (Modéré)'])}")
    fig_tukey.add_hline(y=p_tukey["Moyenne"], line_dash="dot",
                        line_color=THEME["chart"]["colorway"][4],
                        annotation_text=f"Moyenne = {fmt_num(p_tukey['Moyenne'])}")
    plot(fig_tukey, height=450, title="Diagramme de Tukey annoté", showlegend=False)

    st.write("")
    md('<div class="mini-title">Points aberrants identifiés</div>')
    if len(outliers_df) > 0:
        show_table(outliers_df, max_height=300)
    else:
        md(callout("Aucun point aberrant",
                   "Aucune observation ne sort des bornes de Tukey (1.5 × IQR).",
                   "success", "✅"))

    with st.expander("🔬 Comparaison Tukey vs Z-score", expanded=False):
        st.markdown(
            "> Le **Z-score** suppose une distribution approximativement normale et reste "
            "sensible aux valeurs extrêmes. Le critère de **Tukey**, fondé sur l’IQR, est "
            "robuste et ne fait aucune hypothèse sur la distribution."
        )
        seuil_z = st.slider("Seuil |Z|", 2.0, 4.0, 3.0, 0.1)
        z_values = z_scores(serie).abs()
        outliers_z = serie[z_values > seuil_z]
        md(callout(
            "Résultat Z-score",
            f"Points détectés avec |Z| &gt; {seuil_z:.1f} : <b>{len(outliers_z)}</b>.",
            "info", "🔎",
        ))
        if len(outliers_z) > 0:
            show_table(
                df_actuel.loc[outliers_z.index].reset_index(),
                max_height=300,
            )

# -----------------------------------------------------------------------------
# SECTION 7 — Discret vers continu
# -----------------------------------------------------------------------------
elif section == 7:
    md(section_head("🔄", "Transformation discret → continu",
                    "Regroupement d’une variable quantitative en classes, selon les trois règles du TP."))

    serie = df_actuel[colonne_selectionnee].dropna()
    if not callout_num(serie):
        st.stop()

    meth_t = st.radio("Règle de discrétisation",
                      ["sturges", "yule", "fd"], index=0, horizontal=True)
    bornes, nb_k = {
        "sturges": creer_classes_sturges,
        "yule": creer_classes_yule,
        "fd": creer_classes_freedman_diaconis,
    }[meth_t](serie)
    nom_m = {"sturges": "Sturges", "yule": "Yule", "fd": "Freedman–Diaconis"}[meth_t]

    labels_cut = [f"[{bornes[i]:.2f} – {bornes[i + 1]:.2f}]" for i in range(len(bornes) - 1)]
    df_transf = df_actuel.copy()
    df_transf[f"{colonne_selectionnee}_continu"] = pd.cut(
        serie, bins=bornes, include_lowest=True, labels=labels_cut
    )

    counts = df_transf[f"{colonne_selectionnee}_continu"].value_counts().sort_index()
    tab_res = pd.DataFrame({
        "Classe": counts.index,
        "Effectif": counts.values,
        "Fréquence": np.round(counts.values / len(serie), 4),
        "Fréquence (%)": np.round(counts.values / len(serie) * 100, 2),
    })

    left, right = st.columns([1.15, 1.35], gap="large")
    with left:
        md('<div class="mini-title">Tableau discrétisé</div>')
        show_table(tab_res, max_height=360,
                   caption=f"{nom_m} — {nb_k} classes")
        download_csv(tab_res, f"discretisation_{meth_t}.csv",
                     "📥 Exporter le tableau (CSV)", key="dl_cut")

    with right:
        md('<div class="mini-title">Distribution par classe</div>')
        fig_cut = px.bar(
            tab_res,
            x="Classe",
            y="Effectif",
            text="Effectif",
            color="Classe",
            color_discrete_sequence=THEME["chart"]["colorway"],
        )
        fig_cut.update_traces(textposition="outside")
        fig_cut.update_layout(showlegend=False)
        plot(fig_cut, height=360, title=f"Discrétisation de {colonne_selectionnee} ({nom_m})")

    with st.expander("👀 Voir le dataset avec la colonne discrétisée"):
        show_table(
            df_transf[[colonne_selectionnee, f"{colonne_selectionnee}_continu"]].head(20),
            max_height=380,
        )

# -----------------------------------------------------------------------------
# SECTION 8 — Opération inverse
# -----------------------------------------------------------------------------
elif section == 8:
    md(section_head("↩️", "Opération inverse : graphique → tableau",
                    "Reconstituer effectifs, fréquences et type de variable depuis un graphique."))

    mode_inverse = st.selectbox(
        "Type de graphique source",
        [
            "12.1 · Diagramme circulaire",
            "12.2 · Courbe en escalier",
            "12.3 · Histogramme",
        ],
        key="inv_mode",
    )

    if "circulaire" in mode_inverse:
        md(callout("Exemple de la fiche",
                   "Variable <b>Genre</b>, population 50, catégories M / F, "
                   "pourcentages 50 % / 50 %.", "info", "🥧"))
        col1, col2 = st.columns(2, gap="large")
        with col1:
            nom_var = st.text_input("Nom de la variable", "Genre", key="inv_var_pie")
            population = st.number_input("Population totale (n)", min_value=1,
                                         value=50, step=1, key="inv_pop_pie")
        with col2:
            cats_raw = st.text_input("Catégories (séparées par des virgules)", "M, F",
                                     key="inv_cats")
            pct_raw = st.text_input("Pourcentages correspondants (%)", "50, 50",
                                    key="inv_pcts")

        try:
            cats = [c.strip() for c in cats_raw.split(",") if c.strip()]
            pcts = [float(p.strip().replace(",", ".")) for p in pct_raw.split(",") if p.strip()]
            if len(cats) != len(pcts):
                md(callout("Saisie incohérente",
                           "Le nombre de catégories doit égaler le nombre de pourcentages.",
                           "danger", "⛔"))
            else:
                effectifs = [round(p * population / 100) for p in pcts]
                ajustement = population - sum(effectifs)
                if ajustement != 0:
                    effectifs[-1] += ajustement
                frequences = [e / population for e in effectifs]
                tab_reconst = pd.DataFrame({
                    "Modalité": cats,
                    "Pourcentage (%)": pcts,
                    "Effectif reconstitué (n_i)": effectifs,
                    "Fréquence (f_i)": np.round(frequences, 4),
                    "Fréquence cumulée": np.round(np.cumsum(frequences), 4),
                })
                md(callout("Tableau reconstitué",
                           f"Variable <b>{esc(nom_var)}</b> · population <b>{population}</b> · "
                           f"type <b>qualitative</b>.", "success", "✅"))
                show_table(tab_reconst, max_height=320)
                fig_rec = px.pie(tab_reconst, names="Modalité",
                                 values="Effectif reconstitué (n_i)", hole=0.4)
                plot(fig_rec, height=360, title=f"Contrôle visuel — {nom_var}")
        except Exception as exc:  # noqa: BLE001
            md(callout("Erreur de saisie", esc(exc), "danger", "⛔"))

    elif "escalier" in mode_inverse:
        md(callout("Exemple de la fiche",
                   "Variable <b>Âge</b>, n = 50, x = [20, 22, 24, 26, 28], "
                   "F(x) = [0.2, 0.4, 0.7, 0.85, 1.0].", "info", "🪜"))
        col1, col2 = st.columns(2, gap="large")
        with col1:
            nom_var = st.text_input("Nom de la variable", "Age", key="inv_var_step")
            population = st.number_input("Population totale (n)", min_value=1,
                                         value=50, step=1, key="inv_pop_step")
        with col2:
            x_raw = st.text_input("Valeurs x_i", "20, 22, 24, 26, 28", key="inv_x")
            fcum_raw = st.text_input("Fréquences cumulées F(x)", "0.2, 0.4, 0.7, 0.85, 1.0",
                                     key="inv_fcum")

        try:
            x_vals = [float(v.strip()) for v in x_raw.split(",") if v.strip()]
            f_cum_vals = np.array([float(v.strip()) for v in fcum_raw.split(",") if v.strip()])
            if len(x_vals) != len(f_cum_vals):
                md(callout("Saisie incohérente",
                           "Les listes x_i et F(x) doivent avoir la même longueur.",
                           "danger", "⛔"))
            else:
                f_ind = np.diff(np.concatenate([[0.0], f_cum_vals]))
                effectifs = [round(f * population) for f in f_ind]
                ajustement = population - sum(effectifs)
                if ajustement != 0:
                    effectifs[-1] += ajustement

                tab_esc = pd.DataFrame({
                    "Valeur / Modalité (x_i)": x_vals,
                    "Effectif reconstitué (n_i)": effectifs,
                    "Fréquence (f_i)": np.round(np.array(effectifs) / population, 4),
                    "Fréquence cumulée F(x)": np.round(f_cum_vals, 4),
                })
                est_discret = all(float(v).is_integer() for v in x_vals)
                type_txt = "quantitative discrète" if est_discret else "quantitative continue (classes)"
                md(callout("Tableau reconstitué",
                           f"Variable <b>{esc(nom_var)}</b> · population <b>{population}</b> · "
                           f"type <b>{type_txt}</b>.", "success", "✅"))
                show_table(tab_esc, max_height=320)
        except Exception as exc:  # noqa: BLE001
            md(callout("Erreur de saisie", esc(exc), "danger", "⛔"))

    else:
        md(callout("Exemple de la fiche",
                   "Variable <b>Note_Stats</b>, bornes [8, 10, 12, 14, 16, 18, 20], "
                   "effectifs [5, 8, 12, 15, 7, 3].", "info", "📊"))
        col1, col2 = st.columns(2, gap="large")
        with col1:
            nom_var = st.text_input("Nom de la variable", "Note_Stats", key="inv_var_hist")
            bornes_raw = st.text_input("Bornes des classes",
                                       "8, 10, 12, 14, 16, 18, 20", key="inv_bornes")
        with col2:
            eff_raw = st.text_input("Effectifs par classe (n_i)", "5, 8, 12, 15, 7, 3",
                                    key="inv_effs")

        try:
            bornes_list = [float(b.strip()) for b in bornes_raw.split(",") if b.strip()]
            eff_list = [int(float(e.strip())) for e in eff_raw.split(",") if e.strip()]
            if len(bornes_list) - 1 != len(eff_list):
                md(callout("Saisie incohérente",
                           "Le nombre de classes (bornes − 1) doit égaler le nombre d’effectifs.",
                           "danger", "⛔"))
            else:
                population = sum(eff_list)
                frequences = [e / population for e in eff_list] if population else eff_list
                labels = [
                    f"[{bornes_list[i]:.2f} ; {bornes_list[i + 1]:.2f}["
                    for i in range(len(eff_list))
                ]
                tab_hist = pd.DataFrame({
                    "Classe": labels,
                    "Effectif (n_i)": eff_list,
                    "Fréquence (f_i)": np.round(frequences, 4),
                    "Fréquence (%)": np.round(np.array(frequences) * 100, 2),
                    "Fréquence cumulée": np.round(np.cumsum(frequences), 4),
                })
                md(callout("Tableau reconstitué",
                           f"Variable <b>{esc(nom_var)}</b> · population <b>{population}</b> · "
                           f"type <b>quantitative continue</b>.", "success", "✅"))
                show_table(tab_hist, max_height=320)

                fig_hist_rec = go.Figure()
                fig_hist_rec.add_trace(go.Bar(
                    x=labels,
                    y=eff_list,
                    marker_color=THEME["chart"]["colorway"][0],
                    text=eff_list,
                    textposition="outside",
                ))
                plot(fig_hist_rec, height=360, title=f"Histogramme reconstitué — {nom_var}")
        except Exception as exc:  # noqa: BLE001
            md(callout("Erreur de saisie", esc(exc), "danger", "⛔"))

# -----------------------------------------------------------------------------
# SECTION 9 — Synthèse
# -----------------------------------------------------------------------------
elif section == 9:
    md(section_head("🧾", "Synthèse globale",
                    "Rapport automatique sur l’ensemble des variables et aide-mémoire du TP."))

    tab_num, tab_qual, tab_aide = st.tabs([
        "Variables numériques",
        "Variables qualitatives",
        "Aide-mémoire",
    ])

    with tab_num:
        cols_num = [
            c for c in df_actuel.columns
            if np.issubdtype(df_actuel[c].dtype, np.number) and str(c).upper() != "ID"
        ]
        if not cols_num:
            md(callout("Aucune variable numérique",
                       "Le jeu de données ne contient pas de colonne quantitative.",
                       "warn", "⚠️"))
        else:
            rows_num = []
            for colonne in cols_num:
                s = df_actuel[colonne].dropna()
                if len(s) < 2:
                    continue
                q1, q2, q3 = np.percentile(s, [25, 50, 75])
                moyenne = s.mean()
                rows_num.append({
                    "Variable": colonne,
                    "Type": TYPE_META.get(detecter_type_variable(s), TYPE_META["inconnu"])[0],
                    "n": len(s),
                    "Moyenne": round(moyenne, 2),
                    "Médiane": round(q2, 2),
                    "Écart-type": round(s.std(ddof=1), 2),
                    "Étendue": round(s.max() - s.min(), 2),
                    "IQR": round(q3 - q1, 2),
                    "Min": round(s.min(), 2),
                    "Max": round(s.max(), 2),
                    "CV (%)": round(s.std(ddof=1) / moyenne * 100, 2) if moyenne != 0 else np.nan,
                    "Asymétrie": round(s.skew(), 2) if len(s) > 2 else np.nan,
                    "Outliers": len(detecter_points_aberrants(df_actuel, colonne)),
                })
            df_num = pd.DataFrame(rows_num)
            show_table(df_num, max_height=420, caption="Synthèse des variables quantitatives")
            download_csv(df_num, "synthese_numerique.csv",
                         "📥 Exporter la synthèse (CSV)", key="dl_synth_num")

            fig_box = px.box(
                df_actuel[cols_num].melt(var_name="Variable", value_name="Valeur").dropna(),
                x="Variable",
                y="Valeur",
                color="Variable",
                points="outliers",
                color_discrete_sequence=THEME["chart"]["colorway"],
            )
            fig_box.update_layout(showlegend=False)
            plot(fig_box, height=440, title="Boxplots comparatifs des variables numériques")

    with tab_qual:
        cols_qual = [
            c for c in df_actuel.columns
            if str(c).upper() != "ID"
            and (not np.issubdtype(df_actuel[c].dtype, np.number)
                 or df_actuel[c].nunique() <= 10)
        ]
        if not cols_qual:
            md(callout("Aucune variable qualitative",
                       "Le jeu de données ne contient pas de colonne catégorielle.",
                       "warn", "⚠️"))
        else:
            for colonne in cols_qual:
                md(f'<div class="mini-title">Variable — {esc(colonne)}</div>')
                show_table(tableau_qualitatif(df_actuel, colonne), max_height=300)

    with tab_aide:
        st.markdown(r"""
#### Règles de discrétisation

| Règle | Formule | Cas d’usage |
| :--- | :--- | :--- |
| **Sturges** | $k = 1 + 3{,}322 \cdot \log_{10}(n)$ | Distributions proches de la normale, $n < 200$ |
| **Yule** | $k = 2{,}5 \cdot n^{1/4}$ | Distributions quelconques, $n < 1000$ |
| **Freedman–Diaconis** | $h = \dfrac{2 \cdot IQR}{n^{1/3}}$, $k = \left\lceil \dfrac{\max - \min}{h} \right\rceil$ | Robuste aux valeurs aberrantes |
| **Tukey** | $L = Q \pm 1{,}5 \times IQR$ | Détection des points aberrants |

#### Paramètres statistiques

| Catégorie | Paramètre | Interprétation |
| :--- | :--- | :--- |
| **Position** | Moyenne $\bar{x}$ | Centre de gravité, sensible aux valeurs extrêmes |
| **Position** | Médiane $Me$ | Valeur centrale robuste (50 / 50) |
| **Position** | Mode $Mo$ | Valeur ou classe de plus fort effectif |
| **Dispersion** | Étendue $E$ | $x_{max} - x_{min}$ |
| **Dispersion** | IQR | $Q_3 - Q_1$, dispersion des 50 % centraux |
| **Dispersion** | Écart-type $s$ | Dispersion quadratique moyenne |
| **Dispersion** | $CV$ | $s / \bar{x} \times 100$ (dispersion relative) |
| **Quantiles** | Quartiles / déciles | Division en 4 ou 10 parties égales |
| **Forme** | Asymétrie $\gamma_1$ | $>0$ étalée à droite, $<0$ à gauche |
| **Forme** | Aplatissement | Concentration autour de la moyenne |
""")

# -----------------------------------------------------------------------------
# SECTION 10 — Exercices supplémentaires (section 16 de la fiche)
# -----------------------------------------------------------------------------
elif section == 10:
    md(section_head("🧪", "Exercices supplémentaires",
                    "Mise en pratique des huit exercices de la section 16 de la fiche TP."))

    ex1, ex2, ex3, ex4, ex5, ex6, ex7, ex8 = st.tabs([
        "1 · Dataset réel",
        "2 · Trois règles",
        "3 · Outliers",
        "4 · Interpolation",
        "5 · Déciles",
        "6 · Image → tableau",
        "7 · Explorateur",
        "8 · Tukey par groupe",
    ])

    # ---- Exercice 1 : dataset réel ----
    with ex1:
        md(callout("Énoncé",
                   "Chargez un dataset réel (<i>titanic.csv</i>, <i>iris.csv</i>…) et "
                   "appliquez-lui le dashboard complet.", "info", "📘"))
        fichier_ex = st.file_uploader("Dataset réel (CSV / Excel)",
                                      type=["csv", "xlsx", "xls"], key="ex1_file")
        df_ex = df_actuel
        nom_ex = nom_source
        if fichier_ex is not None:
            try:
                loaded = read_uploaded(fichier_ex)
                if loaded is not None and not loaded.empty:
                    df_ex, nom_ex = loaded, fichier_ex.name
            except Exception as exc:  # noqa: BLE001
                md(callout("Lecture impossible", esc(exc), "danger", "⛔"))

        md(callout("Jeu de données analysé",
                   f"<b>{esc(nom_ex)}</b> — {df_ex.shape[0]} lignes × {df_ex.shape[1]} colonnes.",
                   "success", "📁"))

        types_rows = []
        for colonne in df_ex.columns:
            detected = detecter_type_variable(df_ex[colonne])
            label = TYPE_META.get(detected, TYPE_META["inconnu"])[0]
            types_rows.append({"Variable": colonne, "Type détecté": label})
        show_table(pd.DataFrame(types_rows), max_height=320, caption="Classification automatique")

        for colonne in df_ex.columns:
            detected = detecter_type_variable(df_ex[colonne])
            with st.expander(f"📌 {colonne} — {TYPE_META.get(detected, TYPE_META['inconnu'])[0]}"):
                if "qualitative" in detected:
                    show_table(tableau_qualitatif(df_ex, colonne), max_height=320)
                elif np.issubdtype(df_ex[colonne].dtype, np.number) and df_ex[colonne].dropna().shape[0] >= 3:
                    s = df_ex[colonne].dropna()
                    show_table(parametres_table(s), max_height=420)
                    if detected == "quantitative_continue":
                        bornes_ex = _bornes(s, "sturges")
                        fig_ex1 = px.histogram(s, nbins=len(bornes_ex) - 1,
                                               color_discrete_sequence=[THEME["chart"]["colorway"][0]])
                        plot(fig_ex1, height=320, title=f"Distribution — {colonne}")
                    else:
                        counts = s.value_counts().sort_index()
                        fig_ex1 = px.bar(x=counts.index, y=counts.values,
                                         color_discrete_sequence=[THEME["chart"]["colorway"][2]])
                        fig_ex1.update_layout(xaxis_title=colonne,
                                              yaxis_title="Effectif", showlegend=False)
                        plot(fig_ex1, height=320, title=f"Effectifs — {colonne}")
                else:
                    md(callout("Variable non exploitable",
                               "Effectif insuffisant pour cette variable.", "warn", "⚠️"))

    # ---- Exercice 2 : comparaison des trois règles ----
    with ex2:
        md(callout("Énoncé",
                   "Pour une même variable continue, comparez les histogrammes obtenus "
                   "avec les trois règles. Quelle méthode donne la meilleure visualisation ?",
                   "info", "📘"))
        cols_cont = [
            c for c in df_actuel.columns
            if np.issubdtype(df_actuel[c].dtype, np.number) and df_actuel[c].nunique() > 10
        ]
        if not cols_cont:
            md(callout("Aucune variable continue",
                       "Importez un dataset contenant une variable mesurée.", "warn", "⚠️"))
        else:
            var_cont = st.selectbox("Variable continue", cols_cont, key="ex2_var")
            s_cont = df_actuel[var_cont].dropna()

            regles = [
                ("sturges", "Sturges", creer_classes_sturges),
                ("yule", "Yule", creer_classes_yule),
                ("fd", "Freedman–Diaconis", creer_classes_freedman_diaconis),
            ]
            lignes = []
            colonnes_fig = st.columns(3, gap="large")
            for colonne_fig, (code, nom, fonction) in zip(colonnes_fig, regles):
                bornes_r, k_r = fonction(s_cont)
                amplitude = (bornes_r[-1] - bornes_r[0]) / max(k_r, 1)
                lignes.append({
                    "Règle": nom,
                    "Classes (k)": k_r,
                    "Amplitude (h)": round(amplitude, 3),
                    "n / k": round(len(s_cont) / max(k_r, 1), 2),
                })
                with colonne_fig:
                    fig_r = px.histogram(
                        s_cont, nbins=k_r,
                        color_discrete_sequence=[THEME["chart"]["colorway"][regles.index((code, nom, fonction))]],
                    )
                    fig_r.update_traces(
                        xbins=dict(start=bornes_r[0], end=bornes_r[-1], size=amplitude),
                        marker_line_color=THEME["chart"]["pie_line"], marker_line_width=1.2,
                    )
                    plot(fig_r, height=320, title=f"{nom} · k = {k_r}")

            show_table(pd.DataFrame(lignes), max_height=260,
                       caption="Caractéristiques des discrétisations")
            md(callout(
                "Piste de réponse",
                "Freedman–Diaconis adapte la largeur de classe à la forme de la distribution "
                "et reste robuste aux valeurs extrêmes ; Sturges convient aux échantillons "
                "modérés proches de la normale ; Yule produit souvent un nombre de classes "
                "intermédiaire.",
                "info", "💡",
            ))

    # ---- Exercice 3 : outliers sur N(0,1) ----
    with ex3:
        md(callout("Énoncé",
                   "Générez 100 valeurs suivant $N(0,1)$, injectez manuellement trois "
                   "outliers (−8, 10, 15), détectez-les avec Tukey puis avec le Z-score, "
                   "et comparez la robustesse des deux méthodes.", "info", "📘"))

        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            n_sim = st.number_input("Taille de l'échantillon", min_value=20, max_value=5000,
                                    value=100, step=10, key="ex3_n")
        with col_g2:
            seed_sim = st.number_input("Graine aléatoire", min_value=0, max_value=99999,
                                       value=42, step=1, key="ex3_seed")
        with col_g3:
            seuil_z3 = st.slider("Seuil |Z|", 2.0, 4.0, 3.0, 0.1, key="ex3_z")

        generateur = np.random.default_rng(int(seed_sim))
        valeurs = np.concatenate([generateur.normal(0, 1, int(n_sim)), [-8.0, 10.0, 15.0]])
        serie_sim = pd.Series(valeurs, name="Simulation N(0,1) + outliers")

        params_sim = parametres_tukey(serie_sim)
        masque_tukey = (
            (serie_sim < params_sim["L_inf (Modéré)"])
            | (serie_sim > params_sim["L_sup (Modéré)"])
        )
        out_tukey = serie_sim[masque_tukey]
        z_sim = z_scores(serie_sim).abs()
        out_z = serie_sim[z_sim > seuil_z3]

        kpi_row([
            ("Effectif", f"{len(serie_sim)}", f"{int(n_sim)} valeurs + 3 outliers"),
            ("Tukey · détectés", f"{len(out_tukey)}", "critère 1.5 × IQR"),
            (f"Z-score · |Z| > {seuil_z3:.1f}", f"{len(out_z)}", "critère normal"),
            ("Borne L_sup", fmt_num(params_sim["L_sup (Modéré)"]), "Tukey"),
        ])

        comparaison = pd.DataFrame({
            "Méthode": ["Tukey (IQR)", f"Z-score (|Z| > {seuil_z3:.1f})"],
            "Points détectés": [len(out_tukey), len(out_z)],
            "Valeurs": [
                ", ".join(f"{v:g}" for v in out_tukey.values) or "—",
                ", ".join(f"{v:g}" for v in out_z.values) or "—",
            ],
        })
        show_table(comparaison, max_height=240)

        fig_out = go.Figure()
        fig_out.add_trace(go.Scatter(
            x=np.arange(len(serie_sim)), y=serie_sim.values,
            mode="markers", name="Observations",
            marker=dict(size=7, color=THEME["chart"]["colorway"][0], opacity=0.75),
        ))
        fig_out.add_trace(go.Scatter(
            x=np.arange(len(serie_sim))[masque_tukey.values],
            y=serie_sim.values[masque_tukey.values],
            mode="markers", name="Détectés par Tukey",
            marker=dict(size=12, color=THEME["css"]["danger"],
                        symbol="diamond", line=dict(width=1.5, color=THEME["chart"]["pie_line"])),
        ))
        fig_out.add_hline(y=params_sim["L_inf (Modéré)"], line_dash="dash",
                          line_color=THEME["css"]["warning"],
                          annotation_text="L_inf")
        fig_out.add_hline(y=params_sim["L_sup (Modéré)"], line_dash="dash",
                          line_color=THEME["css"]["warning"],
                          annotation_text="L_sup")
        fig_out.update_layout(xaxis_title="Indice", yaxis_title="Valeur")
        plot(fig_out, height=400, title="Outliers injectés — détection de Tukey")

        md(callout(
            "Conclusion attendue",
            "Le Z-score, fondé sur la moyenne et l’écart-type, est lui-même tiré vers le haut "
            "par les valeurs extrêmes : son seuil devient moins discriminant. Le critère de "
            "Tukey, construit sur des quantiles, est <b>robuste</b> et conserve une bonne "
            "sensibilité aux outliers.",
            "success", "🧠",
        ))

    # ---- Exercice 4 : interpolation ----
    with ex4:
        md(callout("Énoncé",
                   "Construisez l’histogramme d’une variable continue, déterminez Q1, Me et Q3 "
                   "par interpolation, puis comparez aux valeurs exactes des données brutes.",
                   "info", "📘"))
        cols_num4 = [
            c for c in df_actuel.columns
            if np.issubdtype(df_actuel[c].dtype, np.number) and df_actuel[c].dropna().shape[0] >= 5
        ]
        if not cols_num4:
            md(callout("Aucune variable numérique", "Importez un dataset adapté.", "warn", "⚠️"))
        else:
            var4 = st.selectbox("Variable", cols_num4, key="ex4_var")
            meth4 = st.radio("Règle", ["sturges", "yule", "fd"], index=0,
                             horizontal=True, key="ex4_meth")
            s4 = df_actuel[var4].dropna()
            res4 = quantiles_par_interpolation(s4, meth4)

            exact4 = {
                "Q1": float(np.percentile(s4, 25)),
                "Me": float(np.percentile(s4, 50)),
                "Q3": float(np.percentile(s4, 75)),
            }
            interp4 = {
                "Q1": res4["Q1"],
                "Me": res4["Me (Q2)"],
                "Q3": res4["Q3"],
            }
            tab4 = pd.DataFrame({
                "Quantile": ["Q1", "Me", "Q3"],
                "Exact (données brutes)": [round(exact4[k], 4) for k in exact4],
                "Interpolé": [round(interp4[k], 4) for k in interp4],
            })
            tab4["Écart"] = (tab4["Interpolé"] - tab4["Exact (données brutes)"]).round(4)
            tab4["Écart relatif (%)"] = (
                (tab4["Écart"].abs() / tab4["Exact (données brutes)"].abs().replace(0, np.nan)) * 100
            ).round(2)
            show_table(tab4, max_height=260)

            bornes4 = res4["bornes"]
            fig4 = go.Figure()
            fig4.add_trace(go.Histogram(
                x=s4, xbins=dict(start=bornes4[0], end=bornes4[-1],
                                 size=float(res4["amplitudes"][0]) if len(res4["amplitudes"]) else None),
                marker=dict(color="rgba(99, 102, 241, 0.55)",
                            line=dict(color=THEME["chart"]["pie_line"], width=1.2)),
                name="Effectifs",
            ))
            for label, valeur, color in [
                ("Q1", res4["Q1"], THEME["css"]["warning"]),
                ("Me", res4["Me (Q2)"], THEME["css"]["danger"]),
                ("Q3", res4["Q3"], THEME["chart"]["colorway"][5]),
            ]:
                fig4.add_vline(x=valeur, line_width=2, line_dash="dash", line_color=color,
                               annotation_text=f"{label} = {valeur:.2f}")
            plot(fig4, height=400, title=f"Interpolation — {var4} ({meth4})")

    # ---- Exercice 5 : déciles ----
    with ex5:
        md(callout("Énoncé",
                   "À partir de la courbe cumulative, déterminez D1, D3, D6 et D9, "
                   "puis interprétez chaque décile.", "info", "📘"))
        cols_num5 = [
            c for c in df_actuel.columns
            if np.issubdtype(df_actuel[c].dtype, np.number) and df_actuel[c].dropna().shape[0] >= 10
        ]
        if not cols_num5:
            md(callout("Aucune variable numérique", "Importez un dataset adapté.", "warn", "⚠️"))
        else:
            var5 = st.selectbox("Variable", cols_num5, key="ex5_var")
            meth5 = st.radio("Règle", ["sturges", "yule", "fd"], index=0,
                             horizontal=True, key="ex5_meth")
            s5 = df_actuel[var5].dropna()

            lignes5 = []
            for k in (1, 3, 6, 9):
                exact = float(np.percentile(s5, k * 10))
                interp = quantile_interpole(s5, k / 10, meth5)
                lignes5.append({
                    "Décile": f"D{k}",
                    "Fréquence cumulée": k / 10,
                    "Exact": round(exact, 4),
                    "Interpolé": round(interp, 4),
                    "Interprétation": f"{k * 10} % des individus ont {var5} ≤ {interp:.2f}",
                })
            tab5 = pd.DataFrame(lignes5)
            show_table(tab5, max_height=280)

            bornes5, f_cum5, _ = courbe_cumulative_quantiles(s5, meth5)
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=bornes5[1:], y=f_cum5, mode="lines+markers",
                line=dict(color=THEME["chart"]["colorway"][1], width=3),
                fill="tozeroy", fillcolor="rgba(6, 182, 212, 0.10)",
                name="F(x)",
            ))
            for k, ligne in zip((1, 3, 6, 9), lignes5):
                valeur = ligne["Interpolé"]
                p = k / 10
                color = THEME["chart"]["colorway"][(k + 1) % 6]
                fig5.add_trace(go.Scatter(
                    x=[bornes5[0], valeur], y=[p, p], mode="lines",
                    line=dict(color=color, width=1.4, dash="dash"),
                    showlegend=False, hoverinfo="skip",
                ))
                fig5.add_trace(go.Scatter(
                    x=[valeur], y=[p], mode="markers+text",
                    marker=dict(size=10, color=color),
                    text=[f"D{k} = {valeur:.2f}"], textposition="top left",
                    showlegend=False,
                ))
            fig5.update_layout(yaxis=dict(range=[0, 1.05], title="Fréquence cumulée"))
            plot(fig5, height=440, title="Déciles sur la courbe cumulative")

    # ---- Exercice 6 : image -> tableau ----
    with ex6:
        md(callout("Énoncé",
                   "À partir d’un diagramme circulaire fourni en image, estimez les "
                   "pourcentages (manuellement ou par analyse d’image avec OpenCV) et "
                   "reconstituez le tableau.", "info", "📘"))
        md(callout(
            "Méthode proposée ici",
            "L’estimation visuelle est reproduite par des curseurs : ajustez la part de "
            "chaque secteur, l’application normalise les pourcentages puis reconstruit "
            "effectifs et fréquences.",
            "info", "🎛️",
        ))

        col_a, col_b = st.columns([1.2, 1.0], gap="large")
        with col_a:
            cats6_raw = st.text_input("Catégories (séparées par des virgules)",
                                      "M, F, Autre", key="ex6_cats")
        with col_b:
            pop6 = st.number_input("Population totale (n)", min_value=1, value=100,
                                   step=1, key="ex6_pop")

        cats6 = [c.strip() for c in cats6_raw.split(",") if c.strip()][:6]
        if not cats6:
            md(callout("Aucune catégorie", "Saisissez au moins une catégorie.", "warn", "⚠️"))
        else:
            valeurs6 = []
            colonnes6 = st.columns(len(cats6))
            for i, (colonne6, cat) in enumerate(zip(colonnes6, cats6)):
                with colonne6:
                    valeurs6.append(st.slider(f"Part — {cat} (%)", 0, 100,
                                              100 // len(cats6), key=f"ex6_{i}"))

            total = sum(valeurs6)
            if total == 0:
                md(callout("Somme nulle", "Réglez au moins un curseur au-dessus de 0.",
                           "warn", "⚠️"))
            else:
                parts = [v / total * 100 for v in valeurs6]
                effectifs6 = [round(p * pop6 / 100) for p in parts]
                ajustement = pop6 - sum(effectifs6)
                if ajustement != 0:
                    effectifs6[-1] += ajustement

                tab6 = pd.DataFrame({
                    "Modalité": cats6,
                    "Part estimée (%)": [round(p, 2) for p in parts],
                    "Effectif reconstitué (n_i)": effectifs6,
                    "Fréquence (f_i)": np.round(np.array(effectifs6) / pop6, 4),
                    "Fréquence cumulée": np.round(np.cumsum(np.array(effectifs6) / pop6), 4),
                })
                md(callout("Tableau reconstitué",
                           f"Population <b>{pop6}</b> · variable <b>qualitative</b>.",
                           "success", "✅"))
                show_table(tab6, max_height=300)
                fig6 = px.pie(tab6, names="Modalité", values="Effectif reconstitué (n_i)",
                              hole=0.4)
                plot(fig6, height=360, title="Diagramme circulaire reconstitué")

    # ---- Exercice 7 : explorateur interactif ----
    with ex7:
        md(callout("Énoncé",
                   "Créer un dashboard interactif où l’utilisateur choisit la variable "
                   "et la méthode de discrétisation.", "info", "📘"))
        var7 = st.selectbox("Variable", list(df_actuel.columns), key="ex7_var")
        type7 = detecter_type_variable(df_actuel[var7])
        md(f'<div style="margin:4px 0 10px;">{badge_html(type7)}</div>')
        s7 = df_actuel[var7].dropna()

        if "qualitative" in type7:
            tab7 = tableau_qualitatif(df_actuel, var7)
            left7, right7 = st.columns(2, gap="large")
            with left7:
                show_table(tab7, max_height=320)
            with right7:
                fig7 = px.pie(tab7, names="Modalité", values="Effectif (n_i)", hole=0.42)
                plot(fig7, height=340, title=f"Répartition — {var7}")
        elif np.issubdtype(df_actuel[var7].dtype, np.number):
            if type7 == "quantitative_discrete":
                tab7 = tableau_quantitatif_discret(df_actuel, var7)
                left7, right7 = st.columns(2, gap="large")
                with left7:
                    show_table(tab7, max_height=320)
                with right7:
                    fig7 = px.bar(tab7, x="Valeur (x_i)", y="Effectif (n_i)",
                                  text="Effectif (n_i)",
                                  color_discrete_sequence=[THEME["chart"]["colorway"][2]])
                    fig7.update_layout(showlegend=False)
                    plot(fig7, height=340, title=f"Effectifs — {var7}")
            else:
                meth7 = st.radio("Règle de discrétisation", ["sturges", "yule", "fd"],
                                 index=0, horizontal=True, key="ex7_meth")
                tab7 = tableau_quantitatif_continu(df_actuel, var7, meth7)
                left7, right7 = st.columns(2, gap="large")
                with left7:
                    show_table(tab7, max_height=340)
                with right7:
                    bornes7 = _bornes(s7, meth7)
                    fig7 = px.histogram(s7, nbins=len(bornes7) - 1,
                                        color_discrete_sequence=[THEME["chart"]["colorway"][0]])
                    plot(fig7, height=340, title=f"Histogramme — {meth7}")
        else:
            md(callout("Variable non exploitable",
                       "Cette colonne ne contient pas de données analysables.", "warn", "⚠️"))

    # ---- Exercice 8 : Tukey par groupe ----
    with ex8:
        md(callout("Énoncé",
                   "Construisez un diagramme de Tukey par groupe (ex. Note_Stats selon Genre) "
                   "et interprétez les différences entre groupes.", "info", "📘"))
        cols_num8 = [c for c in df_actuel.columns
                     if np.issubdtype(df_actuel[c].dtype, np.number)]
        cols_grp8 = [c for c in df_actuel.columns
                     if c not in cols_num8 and df_actuel[c].nunique() <= 12]

        if not cols_num8 or not cols_grp8:
            md(callout("Colonnes insuffisantes",
                       "Il faut au moins une variable quantitative et une variable de groupe "
                       "(≤ 12 modalités).", "warn", "⚠️"))
        else:
            col_y, col_g = st.columns(2)
            with col_y:
                var_y = st.selectbox("Variable quantitative", cols_num8, key="ex8_y")
            with col_g:
                var_g = st.selectbox("Variable de groupe", cols_grp8, key="ex8_g")

            data8 = df_actuel[[var_y, var_g]].dropna()
            fig8 = px.box(
                data8, x=var_g, y=var_y, color=var_g,
                points="all", color_discrete_sequence=THEME["chart"]["colorway"],
            )
            fig8.update_layout(showlegend=False)
            plot(fig8, height=430, title=f"{var_y} selon {var_g}")

            lignes8 = []
            for modalite, groupe in data8.groupby(var_g)[var_y]:
                if len(groupe) < 2:
                    continue
                q1, q2, q3 = np.percentile(groupe, [25, 50, 75])
                lignes8.append({
                    "Groupe": modalite,
                    "n": len(groupe),
                    "Moyenne": round(groupe.mean(), 2),
                    "Médiane": round(q2, 2),
                    "Q1": round(q1, 2),
                    "Q3": round(q3, 2),
                    "IQR": round(q3 - q1, 2),
                    "Écart-type": round(groupe.std(ddof=1), 2),
                })
            show_table(pd.DataFrame(lignes8), max_height=320,
                       caption="Statistiques par groupe")

            md(callout(
                "Lecture",
                "Un décalage des médianes traduit un effet du groupe ; un IQR très différent "
                "signale une hétérogénéité de dispersion. Les points isolés au-delà des "
                "moustaches restent des valeurs à examiner.",
                "info", "💡",
            ))

# -----------------------------------------------------------------------------
# Pied de page
# -----------------------------------------------------------------------------
md(
    '<div class="foot">'
    "AutoSTAT · Dashboard statistique — fiche TP 2025–2026 · "
    "Streamlit · Plotly · Pandas · NumPy"
    "</div>"
)
