"""
pages/3_Sentiment_Analysis.py
-------------------------------
Troisième page de l'application (partie D du lab) : utilise un modèle
de sentiment pré-entraîné HuggingFace pour analyser les avis utilisateurs
des applications retournées par la recherche (page 1).

Pour chaque application sélectionnée :
    - Récupère un échantillon d'avis (utils.get_reviews)
    - Calcule le sentiment de chaque avis (utils.compute_sentiments)
    - Calcule un score de sentiment global par app
    - Affiche un bar chart comparatif des scores de sentiment
    - Permet d'explorer le détail des avis d'une app sélectionnée
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import get_reviews, compute_sentiments, compute_app_sentiment_score, apply_theme

st.set_page_config(page_title="Sentiment Analysis", page_icon="🧠", layout="wide")
apply_theme()

st.title("🧠 Sentiment Analysis")

st.write(
    "Cette page calcule le sentiment des avis utilisateurs (positif / négatif) "
    "pour chaque application retournée par votre recherche, à l'aide du modèle "
    "**distilbert-base-uncased-finetuned-sst-2-english** (HuggingFace)."
)

# --- Vérification : a-t-on des données issues de la recherche ? -------------
if "results_df" not in st.session_state or st.session_state["results_df"].empty:
    st.warning(
        "Aucune donnée disponible. Rendez-vous sur la page **Results Table** "
        "pour effectuer une recherche d'abord."
    )
    st.stop()

results_df = st.session_state["results_df"]

# --- Choix du nombre d'apps à analyser (pour limiter le temps de calcul) -------------
max_apps = st.slider(
    "Nombre d'applications à analyser (les premières du tableau)",
    min_value=1,
    max_value=min(10, len(results_df)),
    value=min(5, len(results_df)),
)
reviews_per_app = st.slider("Nombre d'avis à récupérer par app", min_value=20, max_value=200, value=50, step=10)

apps_to_analyze = results_df.head(max_apps)

run_analysis = st.button("Lancer l'analyse de sentiment", type="primary")

# --- Calcul (mis en cache dans session_state pour ne pas tout recalculer) -------------
if run_analysis:
    sentiment_scores = []
    reviews_by_app = {}

    progress = st.progress(0, text="Démarrage de l'analyse...")

    for i, (_, row) in enumerate(apps_to_analyze.iterrows()):
        app_id = row["appId"]
        title = row["title"]

        progress.progress(
            (i) / len(apps_to_analyze),
            text=f"Récupération des avis pour {title}...",
        )
        review_texts = get_reviews(app_id, count=reviews_per_app)

        progress.progress(
            (i + 0.5) / len(apps_to_analyze),
            text=f"Calcul du sentiment pour {title}...",
        )
        sentiment_df = compute_sentiments(review_texts)
        score = compute_app_sentiment_score(sentiment_df)

        sentiment_scores.append({"appId": app_id, "title": title, "sentiment_score": score, "n_reviews": len(review_texts)})
        reviews_by_app[app_id] = sentiment_df

    progress.progress(1.0, text="Analyse terminée !")

    st.session_state["sentiment_scores_df"] = pd.DataFrame(sentiment_scores)
    st.session_state["reviews_by_app"] = reviews_by_app

# --- Affichage des résultats -------------------------------------------------
if "sentiment_scores_df" in st.session_state:
    scores_df = st.session_state["sentiment_scores_df"]

    st.subheader("📊 Sentiment Score par Application")
    st.caption("Score entre -1 (100% négatif) et +1 (100% positif)")

    chart_df = scores_df.sort_values("sentiment_score")
    fig_sent, ax_sent = plt.subplots(figsize=(8, 0.5 * len(chart_df) + 1))
    bar_colors = ["#f783ac" if v >= 0 else "#ffa8a8" for v in chart_df["sentiment_score"]]
    ax_sent.barh(chart_df["title"], chart_df["sentiment_score"], color=bar_colors)
    ax_sent.set_xlim(-1, 1)
    ax_sent.axvline(0, color="#5c2a3e", linewidth=0.8)
    ax_sent.set_xlabel("Sentiment Score", color="#5c2a3e")
    ax_sent.tick_params(colors="#5c2a3e")
    for spine in ax_sent.spines.values():
        spine.set_color("#ffd6e8")
    fig_sent.tight_layout()
    st.pyplot(fig_sent)

    st.dataframe(
        scores_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "sentiment_score": st.column_config.ProgressColumn(
                "Sentiment Score", min_value=-1, max_value=1, format="%.2f"
            ),
        },
    )

    st.divider()

    # --- Détail des avis pour une app sélectionnée -------------------------------------------------
    st.subheader("🔍 Détail des avis par application")
    selected_title = st.selectbox("Choisissez une application", options=scores_df["title"].tolist())
    selected_app_id = scores_df.loc[scores_df["title"] == selected_title, "appId"].iloc[0]

    detail_df = st.session_state["reviews_by_app"].get(selected_app_id, pd.DataFrame())

    if not detail_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Avis positifs", int((detail_df["label"] == "POSITIVE").sum()))
        with col2:
            st.metric("Avis négatifs", int((detail_df["label"] == "NEGATIVE").sum()))

        st.dataframe(
            detail_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "score": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1, format="%.2f"),
            },
        )
    else:
        st.write("Pas d'avis disponibles pour cette application.")
else:
    st.info("Cliquez sur **Lancer l'analyse de sentiment** pour démarrer.")