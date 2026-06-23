"""
pages/1_Results_Table.py
-------------------------
Première page de l'application : permet à l'utilisateur de saisir un
terme de recherche (par défaut orienté fitness), lance la recherche
d'applications via utils.py, et affiche les résultats sous forme de
tableau (dataframe).

Un filtre Payant / Gratuit permet d'affiner l'affichage des résultats
sans avoir à refaire de recherche.

Les résultats sont stockés dans st.session_state pour pouvoir être
réutilisés par les pages suivantes (Visualizations, Sentiment Analysis)
sans avoir à refaire la requête.
"""

import streamlit as st
from utils import search_apps, apply_theme

st.set_page_config(page_title="Results Table", page_icon="🔎", layout="wide")
apply_theme()

st.title("🔎 Search Results")

st.write(
    "Entrez un terme de recherche lié au fitness (ex: *home workout*, "
    "*fitness tracker*, *yoga app*, *gym workout planner*...) pour récupérer "
    "la liste des applications correspondantes sur le Google Play Store."
)

# --- Formulaire de recherche -------------------------------------------------
with st.form("search_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Search term", value="home fitness apps")
    with col2:
        n_hits = st.number_input("Max results", min_value=5, max_value=50, value=20, step=5)

    submitted = st.form_submit_button("Search", use_container_width=True)
st.caption("don't be shy, type whatever you want")

# --- Exécution de la recherche -------------------------------------------------
if submitted:
    with st.spinner(f"Recherche des applications pour « {query} »..."):
        results_df = search_apps(query=query, country="us", n_hits=n_hits)

    if results_df.empty:
        st.warning("Aucun résultat trouvé pour cette recherche. Essayez un autre terme.")
    else:
        # On persiste les résultats dans la session pour les pages suivantes
        st.session_state["results_df"] = results_df
        st.session_state["search_query"] = query
        st.success(f"{len(results_df)} applications trouvées pour « {query} ».")

# --- Affichage du tableau de résultats -------------------------------------------------
if "results_df" in st.session_state:
    st.subheader(f"Résultats pour : {st.session_state.get('search_query', '')}")

    # --- Filtre Payant / Gratuit -------------------------------------------------
    price_filter = st.radio(
        "Filtrer par prix",
        options=["Toutes", "Gratuites uniquement", "Payantes uniquement"],
        horizontal=True,
    )

    display_df = st.session_state["results_df"]
    if price_filter == "Gratuites uniquement":
        display_df = display_df[display_df["free"] == True]
    elif price_filter == "Payantes uniquement":
        display_df = display_df[display_df["free"] == False]

    if display_df.empty:
        st.warning("Aucune application ne correspond à ce filtre.")
    else:
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "icon": st.column_config.ImageColumn("Icon", width="small"),
                "score": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                "free": st.column_config.CheckboxColumn("Free"),
                "appId": st.column_config.TextColumn("App ID"),
            },
            hide_index=True,
        )

    st.info(
        "Rendez-vous sur la page **Visualizations** ou **Sentiment Analysis** "
        "dans le menu de gauche pour explorer davantage ces résultats."
    )
else:
    st.info("Lancez une recherche ci-dessus pour afficher les résultats.")
st.caption("Wish me good luck on my weight loss journey <3 Allahuma yassir")
