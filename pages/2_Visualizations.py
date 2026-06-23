"""
pages/2_Visualizations.py
---------------------------
Deuxième page de l'application : affiche des visualisations de données
basées sur les résultats de recherche persistés dans session_state
(remplis par la page 1_Results_Table.py).

Contient :
    - Un bar chart pour la distribution des notes (ratings)
    - Un bar chart pour la distribution des genres
    - Un top des apps les mieux notées
    - Un pie chart payant vs gratuit
    - Un word cloud basé sur les descriptions des apps
    - Une sidebar permettant de filtrer les données par App ID
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from utils import apply_theme

st.set_page_config(page_title="Visualizations", page_icon="📈", layout="wide")
apply_theme()

st.title("📈 Data Visualizations")


# --- Vérification : a-t-on des données issues de la recherche ? -------------
if "results_df" not in st.session_state or st.session_state["results_df"].empty:
    st.warning(
        "Aucune donnée disponible. Rendez-vous sur la page **Results Table** "
        "pour effectuer une recherche d'abord."
    )
    st.stop()

df = st.session_state["results_df"].copy()

# --- Sidebar : filtre par App ID -------------------------------------------------
st.sidebar.header("🔍 Filters")
app_ids = df["appId"].dropna().unique().tolist()
selected_apps = st.sidebar.multiselect(
    "Filter by App ID",
    options=app_ids,
    default=app_ids,
)

if selected_apps:
    df = df[df["appId"].isin(selected_apps)]

if df.empty:
    st.warning("Aucune application sélectionnée. Modifiez les filtres dans la sidebar.")
    st.stop()

st.caption(f"Analyse basée sur **{len(df)}** application(s) pour la recherche : "
           f"« {st.session_state.get('search_query', '')} »")

# --- Layout en colonnes pour organiser les visualisations -------------------------------------------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("⭐ Distribution des notes (Ratings)")
    ratings = df["score"].dropna()
    if not ratings.empty:
        st.bar_chart(ratings.round(1).value_counts().sort_index())
    else:
        st.write("Pas de données de notes disponibles.")

with row1_col2:
    st.subheader("📈 Note moyenne du marché")
    avg_score = df["score"].dropna().mean()
    n_rated = df["score"].dropna().shape[0]
    if pd.notna(avg_score):
        st.metric(
            label="Note moyenne (toutes apps confondues)",
            value=f"{avg_score:.2f} ⭐",
            help=f"Calculée sur {n_rated} application(s) notée(s) sur {len(df)} au total.",
        )
        best = df.loc[df["score"].idxmax()]
        worst = df.loc[df["score"].idxmin()]
        st.caption(f"🏅 Meilleure note : **{best['title']}** ({best['score']:.1f}⭐)")
        st.caption(f"🔻 Moins bonne note : **{worst['title']}** ({worst['score']:.1f}⭐)")
    else:
        st.write("Pas de données de notes disponibles.")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("👩‍💻 Développeurs les plus présents")
    dev_counts = df["developer"].value_counts().head(8)
    if not dev_counts.empty:
        st.bar_chart(dev_counts)
    else:
        st.write("Pas de données de développeur disponibles.")

with row2_col2:
    st.subheader("🎯 Note vs. Popularité (installs)")
    scatter_df = df.dropna(subset=["score", "installs"]).copy()
    if not scatter_df.empty:
        # "installs" est une chaîne de type "10,000,000+" -> on la convertit en nombre
        scatter_df["installs_num"] = (
            scatter_df["installs"].astype(str).str.replace(r"[+,]", "", regex=True)
        )
        scatter_df["installs_num"] = pd.to_numeric(scatter_df["installs_num"], errors="coerce")
        scatter_df = scatter_df.dropna(subset=["installs_num"])

        if not scatter_df.empty:
            fig_sc, ax_sc = plt.subplots()
            ax_sc.scatter(scatter_df["installs_num"], scatter_df["score"], color="#d6336c", alpha=0.7)
            ax_sc.set_xscale("log")
            ax_sc.set_xlabel("Nombre d'installations (échelle log)", color="#5c2a3e")
            ax_sc.set_ylabel("Note", color="#5c2a3e")
            ax_sc.tick_params(colors="#5c2a3e")
            for spine in ax_sc.spines.values():
                spine.set_color("#ffd6e8")
            st.pyplot(fig_sc)
        else:
            st.write("Pas assez de données d'installations exploitables.")
    else:
        st.write("Pas de données de popularité disponibles.")

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("🏆 Top Apps par note")
    top_n = st.slider("Nombre d'apps à afficher", min_value=3, max_value=min(15, len(df)), value=min(5, len(df)))
    top_apps = df.dropna(subset=["score"]).sort_values("score", ascending=False).head(top_n)
    st.dataframe(
        top_apps[["title", "developer", "score", "genre"]],
        use_container_width=True,
        hide_index=True,
    )

with row3_col2:
    st.subheader("💰 Paid vs. Free Apps")
    free_counts = df["free"].value_counts().rename({True: "Free", False: "Paid"})
    if not free_counts.empty:
        fig, ax = plt.subplots()
        pink_palette = ["#f783ac", "#ffc9de"]
        ax.pie(
            free_counts.values,
            labels=free_counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=pink_palette[: len(free_counts)],
            textprops={"color": "#5c2a3e"},
        )
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.write("Pas de données disponibles.")

st.divider()

# --- Word Cloud basé sur les descriptions -------------------------------------------------
st.subheader("☁️ Word Cloud des descriptions d'applications")
text_blob = " ".join(df["summary"].dropna().astype(str).tolist())

if text_blob.strip():
    wc = WordCloud(width=1000, height=400, background_color="#fff5f8", colormap="RdPu").generate(text_blob)
    fig_wc, ax_wc = plt.subplots(figsize=(10, 4))
    ax_wc.imshow(wc, interpolation="bilinear")
    ax_wc.axis("off")
    st.pyplot(fig_wc)
else:
    st.write("Pas assez de texte disponible pour générer un word cloud.")
st.caption("💡 Observation : la majorité des apps fitness sont gratuites, ce qui suggère un modèle économique basé sur la publicité ou les achats in-app.")
    
