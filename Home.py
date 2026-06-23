"""
Home.py
-------
Page d'accueil de l'application "Home Workout & Fitness Apps -
Competitor Analysis". Présente le projet à l'utilisateur final avec un
habillage visuel rose pastel sur le thème du sport et du fitness.

C'est aussi le point d'entrée de l'application : c'est ce fichier
qu'on lance avec `streamlit run Home.py`.
"""

import streamlit as st
from utils import apply_theme

st.set_page_config(
    page_title="Fitness Apps - Competitor Analysis",
    page_icon="🏋️‍♀️",
    layout="wide",
)

apply_theme()

# --- Bannière d'introduction -------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <h1>🏋️‍♀️ Fit & Strong — Competitor Analysis 💪</h1>
        <p>Explore, compare et analyse les meilleures applications de sport
        et fitness à domicile, pour t'aider à garder la forme et un beau corps en bonne santé.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="emoji-row">🧘‍♀️ 🏃‍♀️ 🤸‍♀️ 🏋️‍♀️ 🚴‍♀️</div>', unsafe_allow_html=True)

# --- Cartes de fonctionnalités -------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <h4>🔎 Recherche</h4>
            <p>Trouve les applications de fitness les plus pertinentes
            directement depuis le Google Play Store.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <h4>📊 Visualisation</h4>
            <p>Compare les notes, les genres, les apps gratuites et payantes
            grâce à des graphiques clairs et colorés.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <h4>🧠 Sentiment</h4>
            <p>Découvre ce que les utilisatrices et utilisateurs pensent
            vraiment de chaque application, avis par avis.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.markdown(
    "<p style='text-align:center; color:#a64d79;'>"
    "✨ Utilise le menu à gauche pour commencer : "
    "<b>Results Table</b> → <b>Visualizations</b> → <b>Sentiment Analysis</b> ✨"
    "</p>",
    unsafe_allow_html=True,
)