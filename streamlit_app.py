import streamlit as st
import json
import os
import time

# Chemin du fichier pour stocker les joueurs
fichier_joueurs = "joueurs.json"

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

# Charger les joueurs au démarrage
joueurs = charger_joueurs()

# Titre de la page
st.title("Gestion des Joueurs")

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
            with st.spinner(f"Ajout du joueur '{nouveau_joueur}'..."):
                time.sleep(1)  # Simuler un délai de sauvegarde
                joueurs.append(nouveau_joueur)
                sauvegarder_joueurs(joueurs)
            st.success(f"Joueur '{nouveau_joueur}' ajouté avec succès!")
    else:
        st.error("Veuillez entrer un nom de joueur.")
