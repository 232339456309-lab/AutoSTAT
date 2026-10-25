"""
========================================================================================
FICHE TP : DASHBOARD STATISTIQUE ET DÉTERMINATION AUTOMATIQUE DES TYPES DE VARIABLES
========================================================================================
Application Streamlit tout-en-un avec CSS/JS personnalisés, navigation latérale,
chargement de fichier ou données de démonstration du TP, et toutes les visualisations
et calculs statistiques détaillés dans le document 'tp_stat1.pdf'.
========================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# -----------------------------------------------------------------------------
# Configuration de la page Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Statistique Descriptive",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Injection de Styles CSS et Scripts JS Avancés
# -----------------------------------------------------------------------------
CUSTOM_CSS_JS = """
<style>
/* Importation Police Moderne Inter / Outfit */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary: #6366f1;
    --primary-light: #818cf8;
    --primary-dark: #4338ca;
    --secondary: #06b6d4;
    --accent: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --bg-dark: #0f172a;
    --card-bg: rgba(30, 41, 59, 0.7);
    --border-color: rgba(255, 255, 255, 0.08);
}

html, body, [class*="css"] {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* En-tête Hero Stylisé */
.hero-header {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(6, 182, 212, 0.25) 50%, rgba(16, 185, 129, 0.15) 100%);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 25px;
    backdrop-filter: blur(16px);
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
}

.hero-header::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.35) 0%, transparent 70%);
    pointer-events: none;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    margin-top: 8px;
    font-weight: 400;
}

/* Badges Stylisés */
.type-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.badge-nominale { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }
.badge-ordinale { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }
.badge-discrete { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
.badge-continue { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }

/* Cartes Métriques Premium */
.metric-card {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 12px 24px -10px rgba(99, 102, 241, 0.3);
}

.metric-label {
    font-size: 0.85rem;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.05em;
    font-weight: 600;
}

.metric-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #f8fafc;
    margin-top: 6px;
}

.metric-sub {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 4px;
}

/* Boîte de formule mathématique élégante */
.formula-box {
    background: rgba(15, 23, 42, 0.85);
    border-left: 4px solid #6366f1;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin: 15px 0;
    font-size: 0.95rem;
}

/* Callout d'Interprétation */
.interp-box {
    background: linear-gradient(90deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%);
    border-left: 4px solid #10b981;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin: 15px 0;
}

.interp-warning {
    background: linear-gradient(90deg, rgba(245, 158, 11, 0.12) 0%, rgba(239, 68, 68, 0.08) 100%);
    border-left: 4px solid #f59e0b;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin: 15px 0;
}

/* Boutons et Inputs */
.stButton > button {
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.2s ease;
    border: 1px solid rgba(255, 255, 255, 0.15);
}

.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.35);
}

/* Animation douce pour les éléments */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade {
    animation: fadeIn 0.4s ease-out forwards;
}
</style>

<script>
// Petit script JS pour feedback interactif et scroll fluide
document.addEventListener("DOMContentLoaded", function() {
    console.log("Stat Dashboard Initialized with interactive JS features.");
});
</script>
"""
st.markdown(CUSTOM_CSS_JS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 1. Dataset Démo officiel du TP (Listing 2)
# -----------------------------------------------------------------------------
@st.cache_data
def get_demo_dataset():
    """Génère le jeu de données d'exemple fourni dans le TP (Listing 2)"""
    data = {
        'ID': list(range(1, 51)),
        'Genre': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'] * 5,
        'Niveau_Etude': [
            'Licence', 'Master', 'Doctorat', 'Licence', 'Master',
            'Licence', 'Master', 'Doctorat', 'Licence', 'Master'
        ] * 5,
        'Age': [20, 22, 25, 21, 23, 26, 24, 27, 20, 22] * 5,
        'Note_Stats': [12.5, 15.0, 9.5, 17.0, 11.0, 14.5, 13.0, 16.5, 10.5, 18.0] * 5,
        'Heures_Travail': [10, 15, 8, 20, 12, 18, 14, 16, 9, 22] * 5
    }
    return pd.DataFrame(data)


# -----------------------------------------------------------------------------
# 2. Fonctions Métier du TP (Listings 3 à 21)
# -----------------------------------------------------------------------------
def detecter_type_variable(serie: pd.Series) -> str:
    """
    Détecte automatiquement le type statistique d'une variable selon l'algorithme du TP (Listing 3).
    Retourne:
    - 'qualitative_nominale'
    - 'qualitative_ordinale'
    - 'quantitative_discrete'
    - 'quantitative_continue'
    """
    serie_clean = serie.dropna()
    if len(serie_clean) == 0:
        return 'inconnu'

    dtype = serie.dtype
    n_unique = serie_clean.nunique()

    # Si chaîne, booléen, catégorie ou très peu de valeurs uniques
    if dtype in ['object', 'category', 'bool'] or (not np.issubdtype(dtype, np.number) and n_unique < 10):
        categories = serie_clean.unique()
        mots_ordinaux = ['niveau', 'faible', 'moyen', 'eleve', 'licence', 'master', 'doctorat', 'primaire', 'secondaire']
        ordre_possible = any(mot in str(categories).lower() for mot in mots_ordinaux)
        return 'qualitative_ordinale' if ordre_possible else 'qualitative_nominale'

    elif np.issubdtype(dtype, np.number):
        # Vérifie si toutes les valeurs sont entières
        valeurs_entières = np.all(serie_clean == serie_clean.astype(int))
        if valeurs_entières and n_unique <= 20:
            return 'quantitative_discrete'
        else:
            return 'quantitative_continue'

    return 'inconnu'


def tableau_qualitatif(df: pd.DataFrame, colonne: str) -> pd.DataFrame:
    """Génère le tableau statistique qualitatif (Listing 4)"""
    effectifs = df[colonne].value_counts().sort_index()
    frequences = df[colonne].value_counts(normalize=True).sort_index()

    tableau = pd.DataFrame({
        'Modalité': effectifs.index,
        'Effectif (n_i)': effectifs.values,
        'Fréquence (f_i)': np.round(frequences.values, 4),
        'Fréquence (%)': (frequences.values * 100).round(2)
    })
    tableau['Fréquence cumulée'] = tableau['Fréquence (f_i)'].cumsum().round(4)
    tableau['Fréquence cumulée (%)'] = (tableau['Fréquence cumulée'] * 100).round(2)
    return tableau


def tableau_quantitatif_discret(df: pd.DataFrame, colonne: str) -> pd.DataFrame:
    """Génère le tableau statistique quantitatif discret (Listing 5)"""
    effectifs = df[colonne].value_counts().sort_index()
    frequences = df[colonne].value_counts(normalize=True).sort_index()

    tableau = pd.DataFrame({
        'Valeur (x_i)': effectifs.index,
        'Effectif (n_i)': effectifs.values,
        'Fréquence (f_i)': np.round(frequences.values, 4),
        'Fréquence (%)': (frequences.values * 100).round(2),
        'Fréquence cumulée': frequences.values.cumsum().round(4),
        'Fréquence cumulée (%)': (frequences.values.cumsum() * 100).round(2)
    })
    return tableau


# Règles de discrétisation (Listing 6)
def creer_classes_sturges(serie: pd.Series):
    """Règle de Sturges : k = 1 + 3.322 * log10(n)"""
    n = len(serie.dropna())
    nb_classes = max(1, int(np.ceil(1 + 3.322 * np.log10(n))))
    etendue = serie.max() - serie.min()
    amplitude = etendue / nb_classes if nb_classes > 0 else 1
    bornes = [serie.min() + i * amplitude for i in range(nb_classes + 1)]
    bornes[-1] = serie.max()
    return bornes, nb_classes


def creer_classes_yule(serie: pd.Series):
    """Règle de Yule : k = 2.5 * n^(1/4)"""
    n = len(serie.dropna())
    nb_classes = max(1, int(np.ceil(2.5 * (n ** 0.25))))
    etendue = serie.max() - serie.min()
    amplitude = etendue / nb_classes if nb_classes > 0 else 1
    bornes = [serie.min() + i * amplitude for i in range(nb_classes + 1)]
    bornes[-1] = serie.max()
    return bornes, nb_classes


def creer_classes_freedman_diaconis(serie: pd.Series):
    """Règle de Freedman-Diaconis : h = 2 * IQR / n^(1/3)"""
    serie_clean = serie.dropna()
    n = len(serie_clean)
    q25, q75 = np.percentile(serie_clean, [25, 75])
    iqr = q75 - q25
    h = 2 * iqr / (n ** (1 / 3)) if n > 0 else 1
    if h == 0 or np.isnan(h):
        h = (serie_clean.max() - serie_clean.min()) / 10 if (serie_clean.max() - serie_clean.min()) > 0 else 1
    etendue = serie_clean.max() - serie_clean.min()
    nb_classes = max(1, int(np.ceil(etendue / h)))
    bornes = [serie_clean.min() + i * h for i in range(nb_classes + 1)]
    bornes[-1] = serie_clean.max()
    return bornes, nb_classes


def tableau_quantitatif_continu(df: pd.DataFrame, colonne: str, methode: str = 'sturges') -> pd.DataFrame:
    """Tableau de fréquences pour variable continue (Listing 6)"""
    serie = df[colonne].dropna()
    if methode == 'sturges':
        bornes, nb_classes = creer_classes_sturges(serie)
    elif methode == 'yule':
        bornes, nb_classes = creer_classes_yule(serie)
    else:
        bornes, nb_classes = creer_classes_freedman_diaconis(serie)

    effectifs, _ = np.histogram(serie, bins=bornes)
    frequences = effectifs / len(serie)
    frequences_cumulees = np.cumsum(frequences)
    labels = [f"[{bornes[i]:.2f} ; {bornes[i+1]:.2f}]" for i in range(len(bornes) - 1)]

    return pd.DataFrame({
        'Classe': labels,
        'Borne Inf (L_i)': [round(bornes[i], 2) for i in range(len(bornes) - 1)],
        'Borne Sup (L_i+1)': [round(bornes[i+1], 2) for i in range(len(bornes) - 1)],
        'Amplitude (a_i)': [round(bornes[i+1] - bornes[i], 2) for i in range(len(bornes) - 1)],
        'Effectif (n_i)': effectifs,
        'Effectif Cumulé (N_i)': np.cumsum(effectifs),
        'Fréquence (f_i)': frequences.round(4),
        'Fréquence (%)': (frequences * 100).round(2),
        'Fréquence cumulée': frequences_cumulees.round(4),
        'Fréquence cumulée (%)': (frequences_cumulees * 100).round(2)
    })


# Paramètres de Position et Dispersion (Listing 7)
def parametres_position(serie: pd.Series) -> dict:
    serie = serie.dropna()
    mode_val = serie.mode()
    mode_res = mode_val.iloc[0] if len(mode_val) > 0 else np.nan
    return {
        'Effectif (n)': len(serie),
        'Moyenne': serie.mean(),
        'Médiane (Q2)': serie.median(),
        'Mode': mode_res,
        'Minimum': serie.min(),
        'Maximum': serie.max(),
        'Q1 (25%)': np.percentile(serie, 25),
        'Q3 (75%)': np.percentile(serie, 75),
        'D6 (60%)': np.percentile(serie, 60)
    }


def parametres_dispersion(serie: pd.Series) -> dict:
    serie = serie.dropna()
    q1, q3 = np.percentile(serie, [25, 75])
    iqr = q3 - q1
    ecart_type = serie.std(ddof=1) if len(serie) > 1 else 0
    moyenne = serie.mean()
    cv = (ecart_type / moyenne * 100) if moyenne != 0 else np.nan
    return {
        'Étendue': serie.max() - serie.min(),
        'IQR (Q3 - Q1)': iqr,
        'Variance (s²)': serie.var(ddof=1) if len(serie) > 1 else 0,
        'Écart-type (s)': ecart_type,
        'CV (%)': round(cv, 2) if not np.isnan(cv) else np.nan,
        'Asymétrie (Skewness)': serie.skew() if len(serie) > 2 else np.nan,
        'Aplatissement (Kurtosis)': serie.kurtosis() if len(serie) > 3 else np.nan
    }


# Interpolation linéaire sur histogramme (Listing 10)
def quantiles_par_interpolation(serie: pd.Series, methode: str = 'sturges') -> dict:
    serie = serie.dropna()
    n = len(serie)

    if methode == 'sturges':
        bornes, k = creer_classes_sturges(serie)
    elif methode == 'yule':
        bornes, k = creer_classes_yule(serie)
    else:
        bornes, k = creer_classes_freedman_diaconis(serie)

    effectifs, _ = np.histogram(serie, bins=bornes)
    effectifs_cum = np.cumsum(effectifs)
    amplitudes = np.diff(bornes)

    def interpoler(p):
        cible = p * n
        i = np.searchsorted(effectifs_cum, cible, side='left')
        if i >= len(effectifs):
            i = len(effectifs) - 1
        N_avant = 0 if i == 0 else effectifs_cum[i - 1]
        L_i = bornes[i]
        n_i = effectifs[i]
        a_i = amplitudes[i]
        val = L_i + ((cible - N_avant) / n_i) * a_i if n_i > 0 else L_i
        return val, i, L_i, N_avant, n_i, a_i

    q1_val, idx_q1, l_q1, n_av_q1, n_i_q1, a_q1 = interpoler(0.25)
    me_val, idx_me, l_me, n_av_me, n_i_me, a_me = interpoler(0.50)
    q3_val, idx_q3, l_q3, n_av_q3, n_i_q3, a_q3 = interpoler(0.75)
    d6_val, idx_d6, l_d6, n_av_d6, n_i_d6, a_d6 = interpoler(0.60)

    return {
        'Q1': q1_val,
        'Me (Q2)': me_val,
        'D6': d6_val,
        'Q3': q3_val,
        'IQR (Q3 - Q1)': q3_val - q1_val,
        'bornes': bornes,
        'effectifs': effectifs,
        'effectifs_cum': effectifs_cum,
        'amplitudes': amplitudes,
        'details': {
            'Q1': {'idx': idx_q1, 'L_i': l_q1, 'N_avant': n_av_q1, 'n_i': n_i_q1, 'a_i': a_q1, 'p': 0.25},
            'Me': {'idx': idx_me, 'L_i': l_me, 'N_avant': n_av_me, 'n_i': n_i_me, 'a_i': a_me, 'p': 0.50},
            'D6': {'idx': idx_d6, 'L_i': l_d6, 'N_avant': n_av_d6, 'n_i': n_i_d6, 'a_i': a_d6, 'p': 0.60},
            'Q3': {'idx': idx_q3, 'L_i': l_q3, 'N_avant': n_av_q3, 'n_i': n_i_q3, 'a_i': a_q3, 'p': 0.75}
        }
    }


# Courbe cumulative & quantiles (Listing 12)
def courbe_cumulative_quantiles(serie: pd.Series, methode: str = 'sturges'):
    serie = serie.dropna()
    n = len(serie)
    if methode == 'sturges':
        bornes, k = creer_classes_sturges(serie)
    elif methode == 'yule':
        bornes, k = creer_classes_yule(serie)
    else:
        bornes, k = creer_classes_freedman_diaconis(serie)

    effectifs, _ = np.histogram(serie, bins=bornes)
    f_cum = np.cumsum(effectifs) / n
    amplitudes = np.diff(bornes)

    def interpoler(p):
        i = np.searchsorted(f_cum, p, side='left')
        if i >= len(effectifs):
            i = len(effectifs) - 1
        F_avant = 0 if i == 0 else f_cum[i - 1]
        L_i = bornes[i]
        f_i = effectifs[i] / n
        a_i = amplitudes[i]
        return L_i + ((p - F_avant) / f_i) * a_i if f_i > 0 else L_i

    quantiles = {
        'Q1 (25%)': interpoler(0.25),
        'Q2 - Médiane (50%)': interpoler(0.50),
        'D6 (60%)': interpoler(0.60),
        'Q3 (75%)': interpoler(0.75)
    }
    return bornes, f_cum, quantiles


# Paramètres de Tukey et Outliers (Listings 16 & 17)
def parametres_tukey(serie: pd.Series) -> dict:
    serie = serie.dropna()
    q1 = np.percentile(serie, 25)
    q2 = np.percentile(serie, 50)
    q3 = np.percentile(serie, 75)
    iqr = q3 - q1
    l_inf = q1 - 1.5 * iqr
    l_sup = q3 + 1.5 * iqr
    l_inf_ext = q1 - 3.0 * iqr
    l_sup_ext = q3 + 3.0 * iqr

    return {
        'Q1': q1,
        'Q2 (Médiane)': q2,
        'Q3': q3,
        'IQR': iqr,
        'L_inf (Modéré)': l_inf,
        'L_sup (Modéré)': l_sup,
        'L_inf_ext (Extrême)': l_inf_ext,
        'L_sup_ext (Extrême)': l_sup_ext,
        'Min': serie.min(),
        'Max': serie.max(),
        'Moyenne': serie.mean(),
        'Écart-type': serie.std()
    }


def detecter_points_aberrants(df: pd.DataFrame, colonne: str) -> pd.DataFrame:
    serie = df[colonne].dropna()
    p = parametres_tukey(serie)
    outliers = serie[(serie < p['L_inf (Modéré)']) | (serie > p['L_sup (Modéré)'])]

    if len(outliers) == 0:
        return pd.DataFrame(columns=['Index', 'Valeur', 'Type', 'Écart à la médiane', 'Z-Score'])

    types = []
    z_scores = stats.zscore(serie)
    z_map = dict(zip(serie.index, z_scores))

    for idx, val in outliers.items():
        if val < p['L_inf_ext (Extrême)'] or val > p['L_sup_ext (Extrême)']:
            types.append('Extrême (> 3×IQR)')
        else:
            types.append('Modéré (1.5×IQR - 3×IQR)')

    return pd.DataFrame({
        'Index': outliers.index,
        'Valeur': outliers.values,
        'Type': types,
        'Écart à la médiane': (outliers.values - p['Q2 (Médiane)']).round(4),
        'Z-Score': [round(z_map[i], 3) for i in outliers.index]
    })


# -----------------------------------------------------------------------------
# 3. Barre Latérale (Side Menu) & Chargement des Données
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px 0 25px 0;">
        <span style="font-size: 2.5rem;">📊</span>
        <h2 style="margin: 5px 0 0 0; font-weight: 700; color: #818cf8;">StatLab Pro</h2>
        <p style="margin: 0; font-size: 0.8rem; color: #94a3b8;">Fiche TP - Statistique Descriptive</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📁 Source des Données")
    source_choisie = st.radio(
        "Sélectionnez le mode de chargement :",
        ["Jeu de données Démo (TP Stat 1)", "Importer un fichier personnalisé"],
        index=0
    )

    df_actuel = None
    nom_source = ""

    if source_choisie == "Jeu de données Démo (TP Stat 1)":
        df_actuel = get_demo_dataset()
        nom_source = "Dataset Démo TP (N=50 étudiants)"
        st.success("✅ Dataset officiel du TP chargé (50 lignes, 6 colonnes)")
    else:
        fichier = st.file_uploader(
            "Uploadez un fichier (CSV ou Excel)",
            type=['csv', 'xlsx', 'xls']
        )
        if fichier is not None:
            try:
                if fichier.name.endswith('.csv'):
                    # Test délimiteurs courants
                    df_actuel = pd.read_csv(fichier)
                else:
                    df_actuel = pd.read_excel(fichier)
                nom_source = f"Fichier importé : {fichier.name}"
                st.success(f"✅ {fichier.name} chargé ({df_actuel.shape[0]} lignes, {df_actuel.shape[1]} colonnes)")
            except Exception as e:
                st.error(f"Erreur de lecture du fichier : {e}")
                df_actuel = get_demo_dataset()
                nom_source = "Dataset Démo (Secours suite à erreur)"
        else:
            st.info("ℹ️ Veuillez importer un fichier CSV/Excel. Utilisation du dataset Démo par défaut.")
            df_actuel = get_demo_dataset()
            nom_source = "Dataset Démo TP (En attente d'upload)"

    st.markdown("---")
    st.subheader("🎯 Variable d'Étude")

    colonnes_dispos = [col for col in df_actuel.columns if col.upper() != 'ID']
    if not colonnes_dispos:
        colonnes_dispos = list(df_actuel.columns)

    colonne_selectionnee = st.selectbox(
        "Sélectionnez la colonne à analyser :",
        colonnes_dispos,
        index=3 if 'Note_Stats' in colonnes_dispos else 0
    )

    # Détection automatique du type de la colonne sélectionnée
    type_auto = detecter_type_variable(df_actuel[colonne_selectionnee])

    # Possibilité de forcer/ajuster le type si besoin
    st.markdown(f"**Type détecté automatiquement :**")
    badge_map = {
        'qualitative_nominale': ('Qualitative Nominale', 'badge-nominale', '🏷️'),
        'qualitative_ordinale': ('Qualitative Ordinale', 'badge-ordinale', '📈'),
        'quantitative_discrete': ('Quantitative Discrète', 'badge-discrete', '🔢'),
        'quantitative_continue': ('Quantitative Continue', 'badge-continue', '📏')
    }
    label_t, class_t, icon_t = badge_map.get(type_auto, ('Inconnu', 'badge-nominale', '❓'))
    st.markdown(f'<div class="type-badge {class_t}">{icon_t} {label_t}</div>', unsafe_allow_html=True)

    forcer_type = st.checkbox("Modifier manuellement le type de variable ?")
    if forcer_type:
        type_effectif = st.selectbox(
            "Type forcé :",
            ['qualitative_nominale', 'qualitative_ordinale', 'quantitative_discrete', 'quantitative_continue'],
            index=['qualitative_nominale', 'qualitative_ordinale', 'quantitative_discrete', 'quantitative_continue'].index(type_auto)
        )
    else:
        type_effectif = type_auto

    st.markdown("---")
    st.subheader("🧭 Navigation des Sections")
    section_menu = st.radio(
        "Aller à la section :",
        [
            "1. Vue Globale & Détection des Types",
            "2. Tableaux & Graphiques Statistiques",
            "3. Paramètres de Position & Dispersion",
            "4. Interpolation Linéaire sur Histogramme",
            "5. Courbe Cumulative & Quantiles (D6)",
            "6. Diagramme de Tukey & Outliers",
            "7. Discret vers Continu (Discrétisation)",
            "8. Opération Inverse (Graphique → Tableau)",
            "9. Dashboard de Synthèse Global"
        ]
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748b; line-height: 1.4;">
        TP Statistique Descriptive — Année 2025–2026<br>
        Module : Statistique Descriptive (6h)<br>
        <i>Pandas • NumPy • SciPy • Matplotlib • Plotly</i>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Entête Principal Hero
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="hero-header">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
        <div>
            <h1 class="hero-title">Plateforme Statistique & Visualisation Interactive</h1>
            <p class="hero-subtitle">
                Application complète pour le TP Statistique Descriptive • {nom_source}
            </p>
        </div>
        <div>
            <span class="type-badge {class_t}" style="font-size: 0.95rem; padding: 8px 18px;">
                {icon_t} {colonne_selectionnee} : {label_t}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SECTION 1 : VUE GLOBALE & DÉTERMINATION AUTOMATIQUE DES TYPES
# -----------------------------------------------------------------------------
if section_menu.startswith("1."):
    st.markdown("## 🔍 1. Détection Automatique des Types & Aperçu des Données")
    st.markdown(r"""
    Le script applique l'algorithme officiel de la **Fiche TP (Listing 3)** pour classifier automatiquement chaque colonne :
    - **Qualitative Nominale :** Catégories d'objets sans hiérarchie.
    - **Qualitative Ordinale :** Catégories avec hiérarchie ou mots-clés d'ordre (*niveau, licence, master, doctorat, etc.*).
    - **Quantitative Discrète :** Nombres entiers avec nombre fini de valeurs uniques ($\le 20$).
    - **Quantitative Continue :** Nombres réels / mesures continues.
    """)

    # Matrice récapitulative de classification
    summary_data = []
    for col in df_actuel.columns:
        serie = df_actuel[col]
        t = detecter_type_variable(serie)
        lbl, cls, icn = badge_map.get(t, ('Inconnu', 'badge-nominale', '❓'))
        summary_data.append({
            'Colonne': col,
            'Type Détecté': f"{icn} {lbl}",
            'Type Données (dtype)': str(serie.dtype),
            'Valeurs Uniques': serie.nunique(),
            'Valeurs Manquantes': serie.isna().sum(),
            'Exemple de valeurs': str(serie.dropna().unique()[:4].tolist())
        })

    df_summary = pd.DataFrame(summary_data)

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Taille Échantillon (n)</div>
            <div class="metric-value">{len(df_actuel)}</div>
            <div class="metric-sub">Lignes observées</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Nombre de Variables</div>
            <div class="metric-value">{len(df_actuel.columns)}</div>
            <div class="metric-sub">Colonnes dans le dataset</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi3:
        nb_quant = sum(1 for d in summary_data if 'Quantitative' in d['Type Détecté'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Variables Quantitatives</div>
            <div class="metric-value">{nb_quant}</div>
            <div class="metric-sub">Discrètes ou continues</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi4:
        nb_qual = sum(1 for d in summary_data if 'Qualitative' in d['Type Détecté'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Variables Qualitatives</div>
            <div class="metric-value">{nb_qual}</div>
            <div class="metric-sub">Nominales ou ordinales</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📋 Classification des Variables du Dataset")
    st.dataframe(df_summary, use_container_width=True)

    with st.expander("👀 Explorer les données brutes du dataset (premières lignes)", expanded=True):
        st.dataframe(df_actuel.head(15), use_container_width=True)


# -----------------------------------------------------------------------------
# SECTION 2 : TABLEAUX & REPRÉSENTATIONS GRAPHIQUES
# -----------------------------------------------------------------------------
elif section_menu.startswith("2."):
    st.markdown(f"## 📊 2. Tableaux Statistiques & Graphiques pour : `{colonne_selectionnee}`")

    serie_select = df_actuel[colonne_selectionnee]

    # --- VARIABLE QUALITATIVE ---
    if 'qualitative' in type_effectif:
        st.info(f"Variable détectée comme **{label_t}**. Tableaux de fréquences et représentations adaptées (Tuyaux d'orgues & Diagramme Circulaire).")

        tab_stat = tableau_qualitatif(df_actuel, colonne_selectionnee)

        col_t1, col_t2 = st.columns([1.2, 1.8])
        with col_t1:
            st.markdown("### 📑 Tableau Statistique")
            st.dataframe(tab_stat, use_container_width=True)

            # Option téléchargement CSV
            csv = tab_stat.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Télécharger le tableau (CSV)",
                csv,
                f"tableau_{colonne_selectionnee}.csv",
                "text/csv"
            )

        with col_t2:
            st.markdown("### 🥧 Diagramme Circulaire (Section 6.2)")
            fig_pie = px.pie(
                tab_stat,
                names='Modalité',
                values='Effectif (n_i)',
                hole=0.35,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title=f"Répartition de {colonne_selectionnee}"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#1e293b', width=2)))
            fig_pie.update_layout(template="plotly_dark", height=380, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🏛️ Diagramme en Tuyaux d'Orgues (Section 6.1)")
        fig_bar = px.bar(
            tab_stat,
            x='Modalité',
            y='Effectif (n_i)',
            text='Effectif (n_i)',
            color='Modalité',
            color_discrete_sequence=px.colors.qualitative.Vivid,
            title=f"Diagramme en tuyaux d'orgues - {colonne_selectionnee}"
        )
        fig_bar.update_layout(template="plotly_dark", yaxis_title="Effectif (n_i)", xaxis_title=colonne_selectionnee, height=400)
        fig_bar.update_traces(texttemplate='%{text}', textposition='outside', marker_line_color='rgba(255,255,255,0.3)', marker_line_width=1.5)
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- VARIABLE QUANTITATIVE DISCRÈTE ---
    elif type_effectif == 'quantitative_discrete':
        st.info(f"Variable détectée comme **Quantitative Discrète**. Tableaux des effectifs et graphes : Diagramme en Bâtons & Courbe en Escalier.")

        tab_disc = tableau_quantitatif_discret(df_actuel, colonne_selectionnee)

        col_d1, col_d2 = st.columns([1.2, 1.8])
        with col_d1:
            st.markdown("### 📑 Tableau Statistique Discret")
            st.dataframe(tab_disc, use_container_width=True)

        with col_d2:
            st.markdown("### 📌 Diagramme en Bâtons (Section 6.3)")
            fig_baton = go.Figure()
            # Bâtons fins
            for _, row in tab_disc.iterrows():
                fig_baton.add_trace(go.Scatter(
                    x=[row['Valeur (x_i)'], row['Valeur (x_i)']],
                    y=[0, row['Effectif (n_i)']],
                    mode='lines',
                    line=dict(color='#10b981', width=5),
                    showlegend=False
                ))
            fig_baton.add_trace(go.Scatter(
                x=tab_disc['Valeur (x_i)'],
                y=tab_disc['Effectif (n_i)'],
                mode='markers',
                marker=dict(size=12, color='#34d399', line=dict(color='#ffffff', width=2)),
                name='Effectif'
            ))
            fig_baton.update_layout(
                template="plotly_dark",
                title=f"Diagramme en bâtons - {colonne_selectionnee}",
                xaxis_title=colonne_selectionnee,
                yaxis_title="Effectif",
                height=380
            )
            st.plotly_chart(fig_baton, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🪜 Courbe Cumulative en Escalier (Section 6.4)")
        fig_step = go.Figure()
        # Step plot
        fig_step.add_trace(go.Scatter(
            x=tab_disc['Valeur (x_i)'],
            y=tab_disc['Fréquence cumulée'],
            mode='lines+markers',
            line_shape='hv',
            line=dict(color='#f97316', width=3),
            marker=dict(size=8, color='#ef4444'),
            name='F(x)'
        ))
        fig_step.update_layout(
            template="plotly_dark",
            title=f"Fonction de répartition en escalier - {colonne_selectionnee}",
            xaxis_title=colonne_selectionnee,
            yaxis_title="Fréquence cumulée F(x)",
            yaxis=dict(range=[0, 1.05]),
            height=420
        )
        st.plotly_chart(fig_step, use_container_width=True)

    # --- VARIABLE QUANTITATIVE CONTINUE ---
    else:
        st.info("Variable détectée comme **Quantitative Continue**. Comparaison des 3 règles de discrétisation (Sturges, Yule, Freedman-Diaconis), Histogramme et Ogive.")

        regle = st.radio(
            "Choisissez la règle de discrétisation :",
            ["sturges (Sturges : k = 1 + 3.322 log10(n))", "yule (Yule : k = 2.5 * n^(1/4))", "fd (Freedman-Diaconis : h = 2*IQR/n^(1/3))"],
            index=0,
            horizontal=True
        )
        code_regle = regle.split()[0]

        tab_cont = tableau_quantitatif_continu(df_actuel, colonne_selectionnee, methode=code_regle)

        st.markdown(f"### 📑 Tableau des Classes — Règle de {code_regle.upper()}")
        st.dataframe(tab_cont, use_container_width=True)

        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown("### 📊 Histogramme (Section 6.5)")
            if code_regle == 'sturges':
                bornes, _ = creer_classes_sturges(serie_select)
            elif code_regle == 'yule':
                bornes, _ = creer_classes_yule(serie_select)
            else:
                bornes, _ = creer_classes_freedman_diaconis(serie_select)

            fig_hist = px.histogram(
                serie_select,
                nbins=len(bornes) - 1,
                color_discrete_sequence=['#8b5cf6'],
                title=f"Histogramme ({code_regle.upper()}) - {colonne_selectionnee}"
            )
            fig_hist.update_traces(xbins=dict(start=bornes[0], end=bornes[-1], size=(bornes[-1]-bornes[0])/(len(bornes)-1)), marker_line_color='black', marker_line_width=1.5)
            fig_hist.update_layout(template="plotly_dark", yaxis_title="Effectif", xaxis_title=colonne_selectionnee, height=380)
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_c2:
            st.markdown("### 📈 Courbe Cumulative / Ogive (Section 6.6)")
            bornes_og, f_cum_og, _ = courbe_cumulative_quantiles(serie_select, methode=code_regle)

            fig_ogive = go.Figure()
            fig_ogive.add_trace(go.Scatter(
                x=bornes_og[1:],
                y=f_cum_og,
                mode='lines+markers',
                line=dict(color='#06b6d4', width=3),
                fill='tozeroy',
                fillcolor='rgba(6, 182, 212, 0.15)',
                marker=dict(size=8, color='#38bdf8'),
                name='Fréquence cumulée'
            ))
            fig_ogive.update_layout(
                template="plotly_dark",
                title=f"Courbe cumulative (Ogive) - {colonne_selectionnee}",
                xaxis_title=colonne_selectionnee,
                yaxis_title="Fréquence cumulée F(x)",
                yaxis=dict(range=[0, 1.05]),
                height=380
            )
            st.plotly_chart(fig_ogive, use_container_width=True)


# -----------------------------------------------------------------------------
# SECTION 3 : PARAMÈTRES DE POSITION & DISPERSION
# -----------------------------------------------------------------------------
elif section_menu.startswith("3."):
    st.markdown(f"## 📐 3. Paramètres de Position & Dispersion : `{colonne_selectionnee}`")

    serie = df_actuel[colonne_selectionnee].dropna()
    if not np.issubdtype(serie.dtype, np.number):
        st.warning("⚠️ Cette variable est qualitative. Les paramètres numériques sont calculables uniquement sur les variables quantitatives.")
    else:
        p_pos = parametres_position(serie)
        p_disp = parametres_dispersion(serie)

        st.markdown("### 📍 Paramètres de Position (Section 7.1 & 7.2)")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Moyenne (x̄)</div>
                <div class="metric-value">{p_pos['Moyenne']:.2f}</div>
                <div class="metric-sub">Centre de gravité</div>
            </div>
            """, unsafe_allow_html=True)
        with col_p2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Médiane (Me / Q2)</div>
                <div class="metric-value">{p_pos['Médiane (Q2)']:.2f}</div>
                <div class="metric-sub">Valeur 50%</div>
            </div>
            """, unsafe_allow_html=True)
        with col_p3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Mode (Mo)</div>
                <div class="metric-value">{p_pos['Mode']:.2f}</div>
                <div class="metric-sub">Valeur la plus fréquente</div>
            </div>
            """, unsafe_allow_html=True)
        with col_p4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Quartiles Q1 / Q3</div>
                <div class="metric-value">{p_pos['Q1 (25%)']:.1f} / {p_pos['Q3 (75%)']:.1f}</div>
                <div class="metric-sub">25% et 75%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📏 Paramètres de Dispersion & Forme (Section 7.1 & 7.2)")
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Étendue (E)</div>
                <div class="metric-value">{p_disp['Étendue']:.2f}</div>
                <div class="metric-sub">Max - Min</div>
            </div>
            """, unsafe_allow_html=True)
        with col_d2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">IQR (Q3 - Q1)</div>
                <div class="metric-value">{p_disp['IQR (Q3 - Q1)']:.2f}</div>
                <div class="metric-sub">Écart interquartile</div>
            </div>
            """, unsafe_allow_html=True)
        with col_d3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Écart-Type (s)</div>
                <div class="metric-value">{p_disp['Écart-type (s)']:.2f}</div>
                <div class="metric-sub">Variance s² = {p_disp['Variance (s²)']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_d4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Coeff. de Variation</div>
                <div class="metric-value">{p_disp['CV (%)']}%</div>
                <div class="metric-sub">s / x̄ × 100</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📈 Visualisation Graphique des Paramètres (Section 7.3)")

        tab_g1, tab_g2 = st.tabs(["Lignes de Position (Moyenne, Médiane, Q1, Q3)", "Zones de Dispersion (Étendue, IQR, x̄ ± s)"])

        with tab_g1:
            fig_pos = go.Figure()
            fig_pos.add_trace(go.Histogram(
                x=serie,
                name='Distribution',
                marker=dict(color='rgba(99, 102, 241, 0.65)', line=dict(color='black', width=1.5)),
                opacity=0.75
            ))
            # Lignes verticales de position
            fig_pos.add_vline(x=p_pos['Moyenne'], line_width=2.5, line_color="#ef4444", annotation_text=f"Moyenne = {p_pos['Moyenne']:.2f}", annotation_position="top left")
            fig_pos.add_vline(x=p_pos['Médiane (Q2)'], line_width=2.5, line_dash="dash", line_color="#10b981", annotation_text=f"Médiane = {p_pos['Médiane (Q2)']:.2f}", annotation_position="top right")
            fig_pos.add_vline(x=p_pos['Q1 (25%)'], line_width=2, line_dash="dot", line_color="#f59e0b", annotation_text=f"Q1 = {p_pos['Q1 (25%)']:.2f}", annotation_position="bottom left")
            fig_pos.add_vline(x=p_pos['Q3 (75%)'], line_width=2, line_dash="dot", line_color="#a855f7", annotation_text=f"Q3 = {p_pos['Q3 (75%)']:.2f}", annotation_position="bottom right")

            fig_pos.update_layout(
                template="plotly_dark",
                title=f"Paramètres de position annotés sur l'histogramme - {colonne_selectionnee}",
                xaxis_title=colonne_selectionnee,
                yaxis_title="Effectif",
                height=450
            )
            st.plotly_chart(fig_pos, use_container_width=True)

        with tab_g2:
            fig_disp = go.Figure()
            fig_disp.add_trace(go.Histogram(
                x=serie,
                name='Distribution',
                marker=dict(color='rgba(16, 185, 129, 0.55)', line=dict(color='black', width=1.5)),
                opacity=0.75
            ))

            # Zone IQR
            fig_disp.add_vrect(
                x0=p_pos['Q1 (25%)'], x1=p_pos['Q3 (75%)'],
                fillcolor="rgba(59, 130, 246, 0.2)",
                layer="below", line_width=0,
                annotation_text=f"Zone IQR = {p_disp['IQR (Q3 - Q1)']:.2f}",
                annotation_position="top left"
            )

            # Lignes x_bar ± s
            x_bar = p_pos['Moyenne']
            s = p_disp['Écart-type (s)']
            fig_disp.add_vline(x=x_bar, line_width=2, line_color="#ef4444", annotation_text="x̄")
            fig_disp.add_vline(x=x_bar - s, line_width=2, line_dash="dash", line_color="#c084fc", annotation_text="x̄ - s")
            fig_disp.add_vline(x=x_bar + s, line_width=2, line_dash="dash", line_color="#c084fc", annotation_text="x̄ + s")

            fig_disp.update_layout(
                template="plotly_dark",
                title=f"Dispersion : Zone Interquartile et Intervalle [x̄ - s ; x̄ + s] - {colonne_selectionnee}",
                xaxis_title=colonne_selectionnee,
                yaxis_title="Effectif",
                height=450
            )
            st.plotly_chart(fig_disp, use_container_width=True)


# -----------------------------------------------------------------------------
# SECTION 4 : INTERPOLATION LINÉAIRE SUR HISTOGRAMME
# -----------------------------------------------------------------------------
elif section_menu.startswith("4."):
    st.markdown(f"## 📐 4. Détermination de Me, Q1 et Q3 par Interpolation Linéaire sur Histogramme")
    st.markdown("""
    Lorsque les données sont regroupées en classes $[L_i ; L_{i+1}[$, la formule générale d'interpolation linéaire est :
    """)

    st.markdown(r"""
    <div class="formula-box">
        <b>Formule d'Interpolation Linéaire du quantile $Q_p$ :</b><br>
        $$Q_p = L_i + \left( \frac{p \cdot n - N_{i-1}}{n_i} \right) \times a_i$$
        <span style="font-size: 0.85rem; color: #94a3b8;">
        • $L_i$ : borne inférieure de la classe contenant $Q_p$<br>
        • $p$ : rang relatif ($0.25$ pour $Q_1$, $0.50$ pour la Médiane $Me$, $0.75$ pour $Q_3$)<br>
        • $N_{i-1}$ : effectif cumulé avant la classe $i$<br>
        • $n_i$ : effectif de la classe $i$<br>
        • $a_i$ : amplitude de la classe $i$ ($L_{i+1} - L_i$)<br>
        • $n$ : effectif total
        </span>
    </div>
    """, unsafe_allow_html=True)

    serie = df_actuel[colonne_selectionnee].dropna()
    if not np.issubdtype(serie.dtype, np.number):
        st.warning("⚠️ Veuillez sélectionner une variable quantitative.")
    else:
        meth_interp = st.selectbox("Règle de discrétisation pour l'interpolation :", ['sturges', 'yule', 'fd'], index=0)
        res_interp = quantiles_par_interpolation(serie, methode=meth_interp)

        # Tableau détaillé de calcul (Listing 10 & Section 8.3)
        bornes = res_interp['bornes']
        effs = res_interp['effectifs']
        effs_cum = res_interp['effectifs_cum']
        amps = res_interp['amplitudes']

        table_rows = []
        for i in range(len(effs)):
            classe_str = f"[{bornes[i]:.2f} ; {bornes[i+1]:.2f}["
            annotations = []
            if i == res_interp['details']['Q1']['idx']:
                annotations.append("⬅ Classe de Q1")
            if i == res_interp['details']['Me']['idx']:
                annotations.append("⬅ Classe de Me")
            if i == res_interp['details']['Q3']['idx']:
                annotations.append("⬅ Classe de Q3")

            table_rows.append({
                'Classe [Li ; Li+1[': classe_str,
                'Effectif n_i': effs[i],
                'Eff. Cumulé N_i': effs_cum[i],
                'Amplitude a_i': round(amps[i], 2),
                'Repérage des Quantiles': " & ".join(annotations) if annotations else ""
            })

        st.markdown("### 📋 Tableau de Calcul Détaillé (Section 8.3)")
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        col_q1, col_me, col_q3 = st.columns(3)
        with col_q1:
            d = res_interp['details']['Q1']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Q1 Interpolé (25%)</div>
                <div class="metric-value">{res_interp['Q1']:.4f}</div>
                <div class="metric-sub">Classe : [{bornes[d['idx']]:.2f} ; {bornes[d['idx']+1]:.2f}[</div>
            </div>
            """, unsafe_allow_html=True)
        with col_me:
            d = res_interp['details']['Me']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Médiane Interpolée (50%)</div>
                <div class="metric-value">{res_interp['Me (Q2)']:.4f}</div>
                <div class="metric-sub">Classe : [{bornes[d['idx']]:.2f} ; {bornes[d['idx']+1]:.2f}[</div>
            </div>
            """, unsafe_allow_html=True)
        with col_q3:
            d = res_interp['details']['Q3']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Q3 Interpolé (75%)</div>
                <div class="metric-value">{res_interp['Q3']:.4f}</div>
                <div class="metric-sub">Classe : [{bornes[d['idx']]:.2f} ; {bornes[d['idx']+1]:.2f}[</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ⚖️ Comparaison : Valeurs Exactes (Données Brutes) vs Valeurs Interpolées")

        q_exact_q1 = np.percentile(serie, 25)
        q_exact_me = np.percentile(serie, 50)
        q_exact_q3 = np.percentile(serie, 75)
        q_exact_iqr = q_exact_q3 - q_exact_q1

        comp_df = pd.DataFrame({
            'Quantile': ['Q1 (25%)', 'Médiane Me (50%)', 'Q3 (75%)', 'IQR (Q3 - Q1)'],
            'Exact (Données Brutes)': [round(q_exact_q1, 4), round(q_exact_me, 4), round(q_exact_q3, 4), round(q_exact_iqr, 4)],
            f'Interpolé ({meth_interp.upper()})': [
                round(res_interp['Q1'], 4),
                round(res_interp['Me (Q2)'], 4),
                round(res_interp['Q3'], 4),
                round(res_interp['IQR (Q3 - Q1)'], 4)
            ]
        })
        comp_df['Écart Absolu'] = (comp_df[f'Interpolé ({meth_interp.upper()})'] - comp_df['Exact (Données Brutes)']).round(4)
        comp_df['Écart Relatif (%)'] = ((comp_df['Écart Absolu'].abs() / comp_df['Exact (Données Brutes)']) * 100).round(2)

        st.dataframe(comp_df, use_container_width=True)

        st.markdown("### 📊 Histogramme avec Visualisation de l'Interpolation (Section 8.4)")
        fig_int = go.Figure()
        fig_int.add_trace(go.Histogram(
            x=serie,
            xbins=dict(start=bornes[0], end=bornes[-1], size=amps[0]),
            marker=dict(color='rgba(129, 140, 248, 0.65)', line=dict(color='black', width=1.5)),
            name='Effectifs'
        ))
        # Annotations verticales
        fig_int.add_vline(x=res_interp['Q1'], line_width=2.5, line_dash="dash", line_color="#f59e0b", annotation_text=f"Q1 Interp = {res_interp['Q1']:.2f}")
        fig_int.add_vline(x=res_interp['Me (Q2)'], line_width=2.5, line_color="#ef4444", annotation_text=f"Me Interp = {res_interp['Me (Q2)']:.2f}")
        fig_int.add_vline(x=res_interp['Q3'], line_width=2.5, line_dash="dash", line_color="#a855f7", annotation_text=f"Q3 Interp = {res_interp['Q3']:.2f}")

        # Zone IQR
        fig_int.add_vrect(
            x0=res_interp['Q1'], x1=res_interp['Q3'],
            fillcolor="rgba(99, 102, 241, 0.2)",
            layer="below", line_width=0,
            annotation_text=f"IQR Interp = {res_interp['IQR (Q3 - Q1)']:.2f}",
            annotation_position="top left"
        )
        fig_int.update_layout(template="plotly_dark", height=450, title=f"Quantiles déterminés par interpolation sur histogramme - {colonne_selectionnee}")
        st.plotly_chart(fig_int, use_container_width=True)


# -----------------------------------------------------------------------------
# SECTION 5 : COURBE CUMULATIVE & DETERMINATION DE Me, Q1, Q2, Q3, D6
# -----------------------------------------------------------------------------
elif section_menu.startswith("5."):
    st.markdown(f"## 📈 5. Détermination de Me, Q1, Q2, Q3 et D6 à partir de la Courbe Cumulative")
    st.markdown("""
    La **courbe cumulative (Ogive)** représente les fréquences cumulées croissantes.
    Pour lire graphiquement un quantile $Q_p$ :
    1. On trace l'horizontale à la fréquence cumulée cible $p$ ($0.25, 0.50, 0.60, 0.75$).
    2. Elle coupe la courbe en un point d'abscisse $Q_p$.
    3. On projette verticalement sur l'axe des abscisses.
    """)

    serie = df_actuel[colonne_selectionnee].dropna()
    if not np.issubdtype(serie.dtype, np.number):
        st.warning("⚠️ Veuillez sélectionner une variable quantitative.")
    else:
        methode_ogive = st.selectbox("Règle de discrétisation pour l'ogive :", ['sturges', 'yule', 'fd'], index=0)
        bornes, f_cum, quantiles_og = courbe_cumulative_quantiles(serie, methode=methode_ogive)

        # Tableau récapitulatif des quantiles (Section 9.3)
        tab_quantiles = pd.DataFrame([
            {'Quantile': 'Q1', 'Fréquence Cumulée': 0.25, 'Valeur Lue / Interpolée': round(quantiles_og['Q1 (25%)'], 4), 'Interprétation': f"25% des individus ont {colonne_selectionnee} ≤ {quantiles_og['Q1 (25%)']:.2f}"},
            {'Quantile': 'Q2 = Me', 'Fréquence Cumulée': 0.50, 'Valeur Lue / Interpolée': round(quantiles_og['Q2 - Médiane (50%)'], 4), 'Interprétation': f"50% des individus ont {colonne_selectionnee} ≤ {quantiles_og['Q2 - Médiane (50%)']:.2f}"},
            {'Quantile': 'D6 (6e décile)', 'Fréquence Cumulée': 0.60, 'Valeur Lue / Interpolée': round(quantiles_og['D6 (60%)'], 4), 'Interprétation': f"60% des individus ont {colonne_selectionnee} ≤ {quantiles_og['D6 (60%)']:.2f}"},
            {'Quantile': 'Q3', 'Fréquence Cumulée': 0.75, 'Valeur Lue / Interpolée': round(quantiles_og['Q3 (75%)'], 4), 'Interprétation': f"75% des individus ont {colonne_selectionnee} ≤ {quantiles_og['Q3 (75%)']:.2f}"}
        ])

        st.markdown("### 📋 Tableau Récapitulatif des Quantiles (Section 9.3)")
        st.dataframe(tab_quantiles, use_container_width=True)

        # Tracé interactif avec projections horizontales et verticales
        fig_og = go.Figure()
        # Courbe principale
        fig_og.add_trace(go.Scatter(
            x=bornes[1:],
            y=f_cum,
            mode='lines+markers',
            name='Courbe Cumulative',
            line=dict(color='#2dd4bf', width=3),
            fill='tozeroy',
            fillcolor='rgba(45, 212, 191, 0.12)'
        ))

        couleurs_q = {
            'Q1 (25%)': ('#f59e0b', 0.25),
            'Q2 - Médiane (50%)': ('#ef4444', 0.50),
            'D6 (60%)': ('#ec4899', 0.60),
            'Q3 (75%)': ('#8b5cf6', 0.75)
        }

        for nom, (c_hex, p_val) in couleurs_q.items():
            val_x = quantiles_og[nom]
            # Ligne horizontale de projection
            fig_og.add_trace(go.Scatter(
                x=[bornes[0], val_x],
                y=[p_val, p_val],
                mode='lines',
                line=dict(color=c_hex, width=1.5, dash='dash'),
                showlegend=False
            ))
            # Ligne verticale de projection
            fig_og.add_trace(go.Scatter(
                x=[val_x, val_x],
                y=[0, p_val],
                mode='lines',
                line=dict(color=c_hex, width=1.5, dash='dot'),
                showlegend=False
            ))
            # Point d'intersection
            fig_og.add_trace(go.Scatter(
                x=[val_x],
                y=[p_val],
                mode='markers+text',
                marker=dict(size=10, color=c_hex, line=dict(color='white', width=1.5)),
                text=[f"{nom.split()[0]} = {val_x:.2f}"],
                textposition='top left',
                name=nom
            ))

        fig_og.update_layout(
            template="plotly_dark",
            title=f"Lecture Graphique des Quantiles sur la Courbe Cumulative - {colonne_selectionnee}",
            xaxis_title=colonne_selectionnee,
            yaxis_title="Fréquence Cumulée",
            yaxis=dict(range=[0, 1.05]),
            height=500
        )
        st.plotly_chart(fig_og, use_container_width=True)

        # Interprétation automatique (Section 9.6 & Listing 15)
        st.markdown("### 🧠 Interprétation Automatique des Résultats (Section 9.6)")
        moy = serie.mean()
        med = serie.median()
        q1_ex = np.percentile(serie, 25)
        q3_ex = np.percentile(serie, 75)
        iqr_ex = q3_ex - q1_ex
        d6_ex = np.percentile(serie, 60)
        s_std = serie.std()

        # Analyse de la symétrie
        if abs(moy - med) < 0.1 * s_std:
            sym_msg = "Distribution **quasi-symétrique** (Moyenne ≈ Médiane)."
        elif moy > med:
            sym_msg = "Distribution **asymétrique à droite / étalée vers le haut** (Moyenne > Médiane)."
        else:
            sym_msg = "Distribution **asymétrique à gauche / étalée vers le bas** (Moyenne < Médiane)."

        # Analyse de dispersion IQR
        if iqr_ex < s_std:
            disp_msg = "Données **concentrées** autour de la médiane (IQR < écart-type)."
        else:
            disp_msg = "Données **dispersées** dans les 50% centraux (IQR > écart-type)."

        # Dispersion supérieure D6
        if (d6_ex - med) > (q3_ex - med):
            d6_msg = "Forte dispersion dans la partie supérieure (D6 - Me élevé)."
        else:
            d6_msg = "Dispersion modérée dans la partie supérieure."

        st.markdown(f"""
        <div class="interp-box">
            <b>Rapport d'Interprétation Automatique :</b><br>
            • <b>Forme :</b> {sym_msg}<br>
            • <b>Dispersion centrale :</b> {disp_msg} (IQR = {iqr_ex:.2f}, Écart-type = {s_std:.2f})<br>
            • <b>Partie supérieure :</b> {d6_msg} (D6 - Me = {d6_ex - med:.2f})
        </div>
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SECTION 6 : DIAGRAMME DE TUKEY & DÉTECTION DES OUTLIERS
# -----------------------------------------------------------------------------
elif section_menu.startswith("6."):
    st.markdown(f"## 📦 6. Diagramme de Tukey & Détection des Points Aberrants : `{colonne_selectionnee}`")
    st.markdown("""
    Le diagramme de Tukey (Boîte à moustaches / Boxplot) repose sur les quantiles et la règle d'éloignement :
    - **Bornes modérées :** $L_{inf} = Q_1 - 1.5 \times \text{IQR}$ et $L_{sup} = Q_3 + 1.5 \times \text{IQR}$
    - **Bornes extrêmes :** $Q_1 - 3.0 \times \text{IQR}$ et $Q_3 + 3.0 \times \text{IQR}$
    """)

    serie = df_actuel[colonne_selectionnee].dropna()
    if not np.issubdtype(serie.dtype, np.number):
        st.warning("⚠️ Veuillez sélectionner une variable quantitative.")
    else:
        p_tukey = parametres_tukey(serie)
        outliers_df = detecter_points_aberrants(df_actuel, colonne_selectionnee)

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Borne Inf (L_inf)</div>
                <div class="metric-value">{p_tukey['L_inf (Modéré)']:.2f}</div>
                <div class="metric-sub">Q1 - 1.5 × IQR</div>
            </div>
            """, unsafe_allow_html=True)
        with col_t2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Médiane (Q2)</div>
                <div class="metric-value">{p_tukey['Q2 (Médiane)']:.2f}</div>
                <div class="metric-sub">Ligne centrale</div>
            </div>
            """, unsafe_allow_html=True)
        with col_t3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Borne Sup (L_sup)</div>
                <div class="metric-value">{p_tukey['L_sup (Modéré)']:.2f}</div>
                <div class="metric-sub">Q3 + 1.5 × IQR</div>
            </div>
            """, unsafe_allow_html=True)
        with col_t4:
            nb_out = len(outliers_df)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Outliers Détectés</div>
                <div class="metric-value" style="color: {'#ef4444' if nb_out > 0 else '#10b981'};">{nb_out}</div>
                <div class="metric-sub">Points au-delà des bornes</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📊 Boxplot Interactif de Tukey avec Lignes Repères (Section 10.4)")
        fig_tukey = go.Figure()
        fig_tukey.add_trace(go.Box(
            y=serie,
            name=colonne_selectionnee,
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            marker=dict(color='#38bdf8', size=7),
            line=dict(color='#818cf8', width=2),
            fillcolor='rgba(99, 102, 241, 0.3)'
        ))

        # Lignes repères L_inf et L_sup
        fig_tukey.add_hline(y=p_tukey['L_inf (Modéré)'], line_dash="dash", line_color="#f59e0b", annotation_text=f"L_inf = {p_tukey['L_inf (Modéré)']:.2f}")
        fig_tukey.add_hline(y=p_tukey['L_sup (Modéré)'], line_dash="dash", line_color="#f59e0b", annotation_text=f"L_sup = {p_tukey['L_sup (Modéré)']:.2f}")
        fig_tukey.add_hline(y=p_tukey['Moyenne'], line_dash="dot", line_color="#ec4899", annotation_text=f"Moyenne = {p_tukey['Moyenne']:.2f}")

        fig_tukey.update_layout(
            template="plotly_dark",
            title=f"Diagramme de Tukey annoté - {colonne_selectionnee}",
            yaxis_title=colonne_selectionnee,
            height=460
        )
        st.plotly_chart(fig_tukey, use_container_width=True)

        st.markdown("### 🚩 Points Aberrants Identifiés (Critère de Tukey vs Z-Score)")
        if len(outliers_df) > 0:
            st.dataframe(outliers_df, use_container_width=True)
        else:
            st.success("✅ Aucun point aberrant détecté dans cette variable selon le critère de Tukey (1.5×IQR).")

        # Comparaison Tukey vs Z-score (Section 10.5)
        with st.expander("🔬 Comparaison Méthode Tukey vs Méthode Z-Score (Section 10.5)", expanded=False):
            st.markdown("""
            > **Remarque importante (Fiche TP - Section 10.5) :**  
            > La méthode du **Z-Score** suppose une distribution normale et est sensible aux valeurs extrêmes.  
            > La méthode de **Tukey** (fondée sur l'IQR) est **robuste** et ne fait aucune hypothèse sur la distribution.
            """)
            seuil_z = st.slider("Seuil Z-Score pour déclarer un point aberrant :", 2.0, 4.0, 3.0, 0.1)
            z_vals = np.abs(stats.zscore(serie))
            outliers_z = serie[z_vals > seuil_z]
            st.write(f"Points détectés avec |Z-Score| > {seuil_z} : **{len(outliers_z)}** point(s).")
            if len(outliers_z) > 0:
                st.write(df_actuel.loc[outliers_z.index])


# -----------------------------------------------------------------------------
# SECTION 7 : TRANSFORMATION DISCRET -> CONTINU
# -----------------------------------------------------------------------------
elif section_menu.startswith("7."):
    st.markdown(f"## 🔄 7. Transformation d'une Variable Discrète en Continue (Section 11)")
    st.markdown("""
    Cette opération regroupe une variable discrète en classes continues d'intervalles $[L_i ; L_{i+1}]$
    selon l'une des trois règles fondamentales du TP : **Sturges, Yule ou Freedman-Diaconis**.
    """)

    serie = df_actuel[colonne_selectionnee].dropna()
    if not np.issubdtype(serie.dtype, np.number):
        st.warning("⚠️ Veuillez sélectionner une variable quantitative.")
    else:
        meth_t = st.radio("Sélectionnez la règle de discrétisation :", ['sturges', 'yule', 'fd'], index=0, horizontal=True)

        if meth_t == 'sturges':
            bornes, nb_k = creer_classes_sturges(serie)
            nom_m = "Sturges"
        elif meth_t == 'yule':
            bornes, nb_k = creer_classes_yule(serie)
            nom_m = "Yule"
        else:
            bornes, nb_k = creer_classes_freedman_diaconis(serie)
            nom_m = "Freedman-Diaconis"

        labels_cut = [f"[{bornes[i]:.2f} - {bornes[i+1]:.2f}]" for i in range(len(bornes) - 1)]

        df_transf = df_actuel.copy()
        df_transf[f"{colonne_selectionnee}_continu"] = pd.cut(
            serie,
            bins=bornes,
            include_lowest=True,
            labels=labels_cut
        )

        tab_freq_cut = df_transf[f"{colonne_selectionnee}_continu"].value_counts().sort_index()
        tab_res = pd.DataFrame({
            'Classe': tab_freq_cut.index,
            'Effectif': tab_freq_cut.values,
            'Fréquence': (tab_freq_cut.values / len(serie)).round(4),
            'Fréquence (%)': ((tab_freq_cut.values / len(serie)) * 100).round(2)
        })

        col_c1, col_c2 = st.columns([1.2, 1.8])
        with col_c1:
            st.markdown(f"### 📑 Tableau Discrétisé ({nom_m} - {nb_k} classes)")
            st.dataframe(tab_res, use_container_width=True)

        with col_c2:
            st.markdown("### 📊 Distribution par Classe")
            fig_cut = px.bar(
                tab_res,
                x='Classe',
                y='Effectif',
                text='Effectif',
                color='Classe',
                title=f"Discrétisation de {colonne_selectionnee} ({nom_m})"
            )
            fig_cut.update_layout(template="plotly_dark", height=380)
            st.plotly_chart(fig_cut, use_container_width=True)

        with st.expander("👀 Voir le dataset avec la nouvelle colonne discrétisée"):
            st.dataframe(df_transf[[colonne_selectionnee, f"{colonne_selectionnee}_continu"]].head(20), use_container_width=True)


# -----------------------------------------------------------------------------
# SECTION 8 : OPÉRATION INVERSE (GRAPHIQUE -> TABLEAU)
# -----------------------------------------------------------------------------
elif section_menu.startswith("8."):
    st.markdown("## ↩️ 8. Opération Inverse : Reconstitution Graphique $\\rightarrow$ Tableau (Section 12)")
    st.markdown("""
    À partir d'une représentation graphique donnée (ou d'estimations visuelles), cette section permet de reconstituer
    l'effectif total, les effectifs par modalité, les fréquences et la nature de la variable.
    """)

    mode_inverse = st.selectbox(
        "Sélectionnez le type de graphique source à reconstituer :",
        [
            "12.1 Reconstitution depuis un Diagramme Circulaire",
            "12.2 Reconstitution depuis une Courbe en Escalier",
            "12.3 Reconstitution depuis un Histogramme"
        ]
    )

    if "Circulaire" in mode_inverse:
        st.markdown("### 🥧 Reconstitution depuis un Diagramme Circulaire")
        st.markdown("*Exemple par défaut du TP : Variable 'Genre', Population = 50, Catégories = ['M', 'F'], Pourcentages = [50%, 50%]*")

        col_in1, col_in2 = st.columns(2)
        with col_in1:
            nom_var_circ = st.text_input("Nom de la variable :", "Genre")
            pop_circ = st.number_input("Population totale (n) :", min_value=1, value=50, step=1)
        with col_in2:
            cats_input = st.text_input("Catégories (séparées par une virgule) :", "M, F")
            pct_input = st.text_input("Pourcentages correspondants (%) :", "50, 50")

        try:
            cats = [c.strip() for c in cats_input.split(',')]
            pcts = [float(p.strip()) for p in pct_input.split(',')]
            if len(cats) != len(pcts):
                st.error("Le nombre de catégories doit être égal au nombre de pourcentages.")
            else:
                effs = [round(p * pop_circ / 100) for p in pcts]
                diff = pop_circ - sum(effs)
                if diff != 0:
                    effs[-1] += diff

                freqs = [e / pop_circ for e in effs]
                tab_reconst = pd.DataFrame({
                    'Modalité': cats,
                    'Pourcentage (%)': pcts,
                    'Effectif Reconstitué (n_i)': effs,
                    'Fréquence (f_i)': [round(f, 4) for f in freqs],
                    'Fréquence Cumulée': np.cumsum(freqs).round(4)
                })

                st.success(f"Variable : **{nom_var_circ}** | Population : **{pop_circ}** | Type : **Qualitative**")
                st.dataframe(tab_reconst, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur dans les paramètres saisis : {e}")

    elif "Escalier" in mode_inverse:
        st.markdown("### 🪜 Reconstitution depuis une Courbe en Escalier")
        st.markdown("*Exemple du TP (Listing 21) : Variable 'Age', n = 50, x = [20, 22, 24, 26, 28], F(x) = [0.2, 0.4, 0.7, 0.85, 1.0]*")

        col_es1, col_es2 = st.columns(2)
        with col_es1:
            nom_var_esc = st.text_input("Nom de la variable :", "Age")
            pop_esc = st.number_input("Population totale (n) :", min_value=1, value=50, step=1, key="pop_esc")
        with col_es2:
            x_vals_input = st.text_input("Valeurs x_i :", "20, 22, 24, 26, 28")
            fcum_vals_input = st.text_input("Fréquences cumulées F(x) :", "0.2, 0.4, 0.7, 0.85, 1.0")

        try:
            x_vals = [float(x.strip()) for x in x_vals_input.split(',')]
            f_cum = np.array([float(f.strip()) for f in fcum_vals_input.split(',')])

            f_ind = np.diff(np.concatenate([[0], f_cum]))
            effs = [round(f * pop_esc) for f in f_ind]
            diff = pop_esc - sum(effs)
            if diff != 0:
                effs[-1] += diff

            tab_esc = pd.DataFrame({
                'Valeur / Modalité (x_i)': x_vals,
                'Effectif Reconstitué (n_i)': effs,
                'Fréquence (f_i)': [round(e / pop_esc, 4) for e in effs],
                'Fréquence Cumulée F(x)': [round(fc, 4) for fc in f_cum]
            })

            st.success(f"Variable : **{nom_var_esc}** | Population : **{pop_esc}** | Type : **Quantitative Discrète**")
            st.dataframe(tab_esc, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur : {e}")

    else:
        st.markdown("### 📊 Reconstitution depuis un Histogramme")
        st.markdown("*Exemple du TP (Listing 21) : Variable 'Note_Stats', Bornes = [8, 10, 12, 14, 16, 18, 20], Effectifs = [5, 8, 12, 15, 7, 3]*")

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            nom_var_hist = st.text_input("Nom de la variable :", "Note_Stats")
            bornes_input = st.text_input("Bornes des classes (séparées par une virgule) :", "8, 10, 12, 14, 16, 18, 20")
        with col_h2:
            effs_input = st.text_input("Effectifs par classe (n_i) :", "5, 8, 12, 15, 7, 3")

        try:
            b_list = [float(b.strip()) for b in bornes_input.split(',')]
            e_list = [int(e.strip()) for e in effs_input.split(',')]

            if len(b_list) - 1 != len(e_list):
                st.error("Le nombre de classes (bornes - 1) doit correspondre au nombre d'effectifs saisis.")
            else:
                pop_tot = sum(e_list)
                freqs = [e / pop_tot for e in e_list]
                labels = [f"[{b_list[i]:.2f} ; {b_list[i+1]:.2f}[" for i in range(len(e_list))]

                tab_hist_rec = pd.DataFrame({
                    'Classe [Li ; Li+1[': labels,
                    'Effectif (n_i)': e_list,
                    'Fréquence (f_i)': [round(f, 4) for f in freqs],
                    'Fréquence (%)': [round(f * 100, 2) for f in freqs],
                    'Fréquence Cumulée': np.cumsum(freqs).round(4)
                })

                st.success(f"Variable : **{nom_var_hist}** | Population Totale Reconstituée : **{pop_tot}** | Type : **Quantitative Continue**")
                st.dataframe(tab_hist_rec, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur : {e}")


# -----------------------------------------------------------------------------
# SECTION 9 : DASHBOARD DE SYNTHÈSE GLOBAL
# -----------------------------------------------------------------------------
elif section_menu.startswith("9."):
    st.markdown("## 📑 9. Dashboard de Synthèse Global (Section 13, 14 & 15)")
    st.markdown("""
    Rapport d'analyse statistique complet généré automatiquement pour l'ensemble des variables du dataset.
    """)

    tab_syn1, tab_syn2, tab_syn3 = st.tabs([
        "📋 Synthèse des Variables Numériques",
        "🏷️ Synthèse des Variables Qualitatives",
        "📚 Aide-Mémoire & Formules du TP"
    ])

    with tab_syn1:
        cols_num = [c for c in df_actuel.columns if np.issubdtype(df_actuel[c].dtype, np.number) and c.upper() != 'ID']
        if cols_num:
            rows_num = []
            for c in cols_num:
                s = df_actuel[c].dropna()
                q1, q2, q3 = np.percentile(s, [25, 50, 75])
                iqr = q3 - q1
                rows_num.append({
                    'Variable': c,
                    'Type': detecter_type_variable(s),
                    'n': len(s),
                    'Moyenne': round(s.mean(), 2),
                    'Médiane': round(q2, 2),
                    'Écart-type': round(s.std(), 2),
                    'Étendue': round(s.max() - s.min(), 2),
                    'IQR': round(iqr, 2),
                    'Min': round(s.min(), 2),
                    'Max': round(s.max(), 2),
                    'CV (%)': round(s.std() / s.mean() * 100, 2) if s.mean() != 0 else np.nan,
                    'Asymétrie': round(s.skew(), 2),
                    'Outliers': len(detecter_points_aberrants(df_actuel, c))
                })
            st.dataframe(pd.DataFrame(rows_num), use_container_width=True)

            st.markdown("### 📊 Comparaison Visuelle des Distributions")
            fig_multi_box = px.box(
                df_actuel[cols_num],
                points="all",
                title="Boxplots Comparatifs des Variables Numériques",
                template="plotly_dark"
            )
            fig_multi_box.update_layout(height=450)
            st.plotly_chart(fig_multi_box, use_container_width=True)
        else:
            st.info("Aucune variable numérique disponible.")

    with tab_syn2:
        cols_qual = [c for c in df_actuel.columns if not np.issubdtype(df_actuel[c].dtype, np.number) or c.upper() == 'ID']
        cols_qual = [c for c in cols_qual if c.upper() != 'ID']
        if cols_qual:
            for cq in cols_qual:
                st.markdown(f"#### Variable : `{cq}`")
                st.dataframe(tableau_qualitatif(df_actuel, cq), use_container_width=True)
        else:
            st.info("Aucune variable qualitative dans le dataset.")

    with tab_syn3:
        st.markdown(r"""
        ### 📖 Synthèse des Règles de Discrétisation (Section 14)
        | Règle | Formule | Cas d'Usage |
        | :--- | :--- | :--- |
        | **Sturges** | $k = 1 + 3.322 \cdot \log_{10}(n)$ | Distributions proches de la loi normale, $n < 200$ |
        | **Yule** | $k = 2.5 \cdot n^{1/4}$ | Distributions quelconques, $n < 1000$ |
        | **Freedman–Diaconis** | $h = \frac{2 \cdot \text{IQR}}{n^{1/3}}$, $k = \lceil \frac{\max - \min}{h} \rceil$ | Robuste aux valeurs aberrantes (outliers) |
        | **Tukey (Détection)** | $L = Q \pm 1.5 \times \text{IQR}$ | Détection robuste des points aberrants |

        ### 📖 Synthèse des Paramètres Statistiques (Section 15)
        | Catégorie | Paramètre | Signification & Rôle |
        | :--- | :--- | :--- |
        | **Position** | Moyenne $\bar{x}$ | Centre de gravité, sensible aux valeurs extrêmes |
        | **Position** | Médiane $Me$ | Valeur séparant l'échantillon en deux moitiés égales (50% / 50%), robuste |
        | **Position** | Mode $Mo$ | Valeur ou classe ayant le plus fort effectif |
        | **Dispersion** | Étendue $E$ | Amplitude globale $x_{max} - x_{min}$ |
        | **Dispersion** | IQR ($Q_3 - Q_1$) | Dispersion des 50% d'individus centraux, insensible aux outliers |
        | **Dispersion** | Écart-type $s$ | Dispersion quadratique moyenne autour de la moyenne |
        | **Dispersion** | Coeff. de Variation $CV$ | Dispersion relative : $s / \bar{x} \times 100\%$ |
        | **Forme** | Asymétrie (Skewness $\gamma_1$) | $\gamma_1 > 0$ étalé à droite, $\gamma_1 < 0$ étalé à gauche, $\gamma_1 \approx 0$ symétrique |
        | **Forme** | Aplatissement (Kurtosis) | Degré de concentration autour du centre comparé à la loi normale |
        """)

# -----------------------------------------------------------------------------
# Pied de page
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 15px 0;">
    Dashboard Statistique Descriptive • Conforme à la Fiche TP 2025–2026 • Réalisé avec Streamlit, Plotly, Pandas & NumPy
</div>
""", unsafe_allow_html=True)
