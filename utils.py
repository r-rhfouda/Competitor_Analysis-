"""
utils.py
--------
Ce fichier regroupe toutes les fonctions de récupération et de traitement
des données utilisées par les différentes pages de l'application
"Home Workout & Fitness Apps - Competitor Analysis" :

    1. Recherche d'applications sur le Google Play Store (API-based, via
       la librairie google-play-scraper, gratuite et sans clé API).
    2. Récupération des avis (reviews) d'une application donnée.
    3. Calcul du sentiment des avis à l'aide d'un modèle pré-entraîné
       HuggingFace (utilisé dans la page 3 - Sentiment Analysis).

Note pédagogique : google-play-scraper fonctionne en récupérant les pages
publiques du Google Play Store (pas une API officielle Google, mais une
librairie open-source largement utilisée). Elle ne nécessite ni clé API,
ni compte développeur, ni paiement.

Toutes les fonctions coûteuses en temps (appels réseau, chargement du
modèle ML) sont mises en cache avec st.cache_data / st.cache_resource
pour éviter de refaire le travail à chaque interaction utilisateur.
"""

import pandas as pd
import streamlit as st
from google_play_scraper import search, reviews, Sort


# ---------------------------------------------------------------------
# 0. STYLE PARTAGE (theme rose pastel applique sur toutes les pages)
# ---------------------------------------------------------------------
def apply_theme():
    """
    Injecte le CSS partagé (rose pastel + cartes) utilisé par toutes les
    pages de l'application, pour garder un visuel cohérent.

    Le texte est volontairement en mauve foncé (#5c2a3e) sur fond clair
    pour garantir un bon contraste (un texte blanc sur fond rose pastel
    n'est pas assez lisible).
    """
    st.markdown(
        """
        <style>
        h1, h2, h3 {
            color: #d6336c !important;
        }
        .hero-banner {
            background: linear-gradient(135deg, #ffd6e8 0%, #ffeef5 100%);
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1.2rem;
        }
        .hero-banner h1 {
            font-size: 2.1rem;
            margin-bottom: 0.4rem;
            color: #d6336c !important;
        }
        .hero-banner p {
            color: #a64d79 !important;
            font-size: 1.05rem;
        }
        .feature-card {
            background-color: #ffeef5;
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid #ffd6e8;
            height: 100%;
        }
        .feature-card h4 {
            color: #d6336c !important;
            margin-top: 0;
        }
        .feature-card p {
            color: #5c2a3e !important;
        }
        .emoji-row {
            font-size: 1.8rem;
            text-align: center;
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# 1. RECHERCHE D'APPLICATIONS (équivalent du Lab 1 - code API-based)
# ---------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def search_apps(query: str, country: str = "us", lang: str = "en", n_hits: int = 20) -> pd.DataFrame:
    """
    Prend un terme de recherche et retourne un DataFrame avec les
    applications correspondantes trouvées sur le Google Play Store.

    Paramètres
    ----------
    query : str
        Le terme de recherche saisi par l'utilisateur
        (ex: "home workout fitness apps").
    country : str
        Code pays pour le store (ex: "us", "fr").
    lang : str
        Code langue pour les résultats (ex: "en", "fr").
    n_hits : int
        Nombre maximum de résultats à récupérer.

    Retour
    ------
    pd.DataFrame
        Un DataFrame contenant, pour chaque application : appId, title,
        developer, score (note), price, free (gratuite ou non), genre,
        installs, icon (url de l'icône), summary (description courte).
    """
    if not query or not query.strip():
        return pd.DataFrame()

    results = search(
        query,
        lang=lang,
        country=country,
        n_hits=n_hits,
    )

    rows = []
    for app in results:
        rows.append({
            "appId": app.get("appId"),
            "title": app.get("title"),
            "developer": app.get("developer"),
            "score": app.get("score"),
            "free": app.get("free"),
            "price": app.get("price"),
            "currency": app.get("currency"),
            "genre": app.get("genre"),
            "installs": app.get("installs", "N/A"),
            "icon": app.get("icon"),
            "summary": app.get("summary", ""),
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# 2. RECUPERATION DES AVIS (REVIEWS) D'UNE APPLICATION
# ---------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_reviews(app_id: str, lang: str = "en", country: str = "us", count: int = 100) -> list[str]:
    """
    Prend un appId et retourne une liste de contenus d'avis utilisateurs
    (un échantillon, suffisant pour une analyse de sentiment).

    Paramètres
    ----------
    app_id : str
        L'identifiant de l'application (ex: "com.freeletics.fl").
    lang, country : str
        Langue et pays utilisés pour filtrer les avis.
    count : int
        Nombre d'avis à récupérer (un échantillon raisonnable, ex: 100).

    Retour
    ------
    list[str]
        Liste des textes des avis (contenu uniquement).
    """
    if not app_id:
        return []

    try:
        result, _ = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=count,
        )
    except Exception as e:
        st.warning(f"Impossible de récupérer les avis pour {app_id}: {e}")
        return []

    return [r["content"] for r in result if r.get("content")]


# ---------------------------------------------------------------------
# 3. ANALYSE DE SENTIMENT (modèle pré-entraîné HuggingFace)
# ---------------------------------------------------------------------
@st.cache_resource(show_spinner="Chargement du modèle de sentiment...")
def load_sentiment_model():
    """
    Charge (une seule fois grâce au cache) le pipeline de classification
    de sentiment HuggingFace.

    Modèle choisi : distilbert-base-uncased-finetuned-sst-2-english
    -> Modèle léger, rapide, entraîné pour la classification binaire
       de sentiment (POSITIVE / NEGATIVE), adapté à des avis utilisateurs
       courts en anglais (ex: "this app crashes constantly", "great workouts!").
    """
    from transformers import pipeline
    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )


def compute_sentiments(review_list: list[str]) -> pd.DataFrame:
    """
    Calcule le sentiment (label + score de confiance) pour chaque avis
    d'une liste donnée.

    Paramètres
    ----------
    review_list : list[str]
        Liste de textes d'avis.

    Retour
    ------
    pd.DataFrame
        Colonnes : review, label (POSITIVE/NEGATIVE), score (confiance 0-1).
    """
    if not review_list:
        return pd.DataFrame(columns=["review", "label", "score"])

    classifier = load_sentiment_model()

    # Le modèle a une limite de tokens : on tronque les avis trop longs
    truncated = [r[:512] for r in review_list]
    predictions = classifier(truncated)

    rows = [
        {"review": review, "label": pred["label"], "score": pred["score"]}
        for review, pred in zip(review_list, predictions)
    ]
    return pd.DataFrame(rows)


def compute_app_sentiment_score(sentiment_df: pd.DataFrame) -> float:
    """
    Calcule un score de sentiment global pour une application à partir
    du DataFrame de sentiments par avis (compute_sentiments).

    Le score est calculé comme : (% d'avis positifs) - (% d'avis négatifs),
    une valeur entre -1 (tout négatif) et +1 (tout positif).
    """
    if sentiment_df.empty:
        return 0.0

    total = len(sentiment_df)
    positive = (sentiment_df["label"] == "POSITIVE").sum()
    negative = (sentiment_df["label"] == "NEGATIVE").sum()

    return round((positive - negative) / total, 3)