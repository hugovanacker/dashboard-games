import streamlit as st
import json
import os
from datetime import datetime

# Chemin du fichier pour stocker les joueurs
fichier_joueurs = "joueurs.json"

# Chemin du fichier pour stocker les parties
fichier_parties = "parties.json"

# Fonction pour charger les joueurs depuis le fichier
def charger_joueurs():
    if os.path.exists(fichier_joueurs):
        with open(fichier_joueurs, "r") as f:
            return json.load(f)
    return []

# Fonction pour sauvegarder les joueurs dans le fichier
def sauvegarder_joueurs(joueurs):
    with open(fichier_joueurs, "w") as f:
        json.dump(joueurs, f)

# Fonction pour charger les parties depuis le fichier
def charger_parties():
    if os.path.exists(fichier_parties):
        with open(fichier_parties, "r") as f:
            return json.load(f)
    return []

# Fonction pour sauvegarder les parties dans le fichier
def sauvegarder_parties(parties):
    with open(fichier_parties, "w") as f:
        json.dump(parties, f)

# Charger les joueurs et les parties au démarrage
joueurs = charger_joueurs()
parties = charger_parties()

# Sidebar pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Résultats", "Ajouter un joueur", "Ajouter une partie"], index=0)

# Page "Résultats"
if page == "Résultats":
    st.title("Résultats")
    st.write("Voici le tableau des résultats :")
    st.table([])

# Page "Ajouter un joueur"
elif page == "Ajouter un joueur":
    st.title("Ajouter un Joueur")

    # Afficher la liste des joueurs horizontalement dans un tableau
    st.header("Liste des Joueurs")
    if joueurs:
        cols = st.columns(len(joueurs))
        for col, joueur in zip(cols, joueurs):
            col.markdown(f"**{joueur}**")
    else:
        st.write("Aucun joueur n'est encore ajouté.")

    # Formulaire pour ajouter un joueur
    st.header("Ajouter un Joueur")
    nouveau_joueur = st.text_input("Nom du joueur")
    if st.button("Ajouter"):
        if nouveau_joueur:
            if nouveau_joueur in joueurs:
                st.error(f"Le joueur '{nouveau_joueur}' est déjà présent dans la liste.")
            else:
                joueurs.append(nouveau_joueur)
                sauvegarder_joueurs(joueurs)
                st.success(f"Joueur '{nouveau_joueur}' ajouté avec succès!")
        else:
            st.error("Veuillez entrer un nom de joueur.")

# Page "Ajouter une partie"
elif page == "Ajouter une partie":
    st.title("Ajouter une Partie")

    # Formulaire pour ajouter une partie
    nom_jeu = st.text_input("Nom du jeu")
    date_partie = st.date_input("Date de la partie", datetime.today())
    nombre_joueurs = st.number_input("Nombre de joueurs", min_value=1, value=1)

    results = {}
    for i in range(1, nombre_joueurs + 1):
        joueur = st.selectbox(f"Joueur à la position {i}", [""] + joueurs)
        results[f"Position {i}"] = joueur

    if st.button("Ajouter la partie"):
        if nom_jeu and all(results.values()):
            nouvelle_partie = {
                "nom_jeu": nom_jeu,
                "date": date_partie.strftime("%Y-%m-%d"),
                "resultats": results
            }
            parties.append(nouvelle_partie)
            sauvegarder_parties(parties)
            st.success("Partie ajoutée avec succès!")
        else:
            st.error("Veuillez remplir tous les champs.")
