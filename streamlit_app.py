import streamlit as st
import json
import os
from datetime import datetime
import uuid

# Chemin du fichier pour stocker les joueurs
fichier_joueurs = "joueurs.json"

# Chemin du fichier pour stocker les résultats des parties
fichier_resultats = "results.json"

# Mot de passe pour accéder aux autres onglets
mot_de_passe = "kakoukakou"

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

# Fonction pour charger les résultats des parties depuis le fichier
def charger_resultats():
    if os.path.exists(fichier_resultats):
        with open(fichier_resultats, "r") as f:
            return json.load(f)
    return []

# Fonction pour sauvegarder les résultats des parties dans le fichier
def sauvegarder_resultats(resultats):
    with open(fichier_resultats, "w") as f:
        json.dump(resultats, f)

# Charger les joueurs et les résultats des parties au démarrage
joueurs = charger_joueurs()
resultats = charger_resultats()

# Fonction pour vérifier le mot de passe
def verifier_mot_de_passe():
    if "mot_de_passe_valide" not in st.session_state:
        st.session_state.mot_de_passe_valide = False

    if not st.session_state.mot_de_passe_valide:
        mot_de_passe_entree = st.text_input("Entrez le mot de passe", type="password")
        if st.button("Valider"):
            if mot_de_passe_entree == mot_de_passe:
                st.session_state.mot_de_passe_valide = True
                st.success("Mot de passe correct.")
            else:
                st.error("Mot de passe incorrect.")
        return False
    return True

# Sidebar pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Résultats", "Ajouter un joueur", "Ajouter une partie"], index=0)

# Page "Résultats"
if page == "Résultats":
    st.title("Résultats")

    # Section "Classement"
    st.header("Classement")

    # Calculer le classement des joueurs
    classement = {}
    for resultat in resultats:
        joueur = resultat["joueur"]
        position = resultat["position"]
        if joueur not in classement:
            classement[joueur] = 0
        classement[joueur] += 1 / position  # Plus la position est basse, plus le score est élevé

    # Trier le classement par score décroissant
    classement_trie = sorted(classement.items(), key=lambda x: x[1], reverse=True)

    # Afficher le classement
    if classement_trie:
        for joueur, score in classement_trie:
            st.write(f"**{joueur}:** {score:.2f} points")
    else:
        st.write("Aucun classement disponible.")

    # Section "Dernières parties"
    st.header("Dernières parties")

    # Sélecteur pour filtrer les parties contenant exactement les joueurs sélectionnés
    joueurs_selectionnes = st.multiselect("Sélectionner les joueurs", joueurs)

    # Filtrer les résultats en fonction des joueurs sélectionnés
    if joueurs_selectionnes:
        # Construire un mapping party_key -> liste de joueurs
        # party_key = partie_id si disponible, sinon 'partie|date' (fallback pour anciennes entrées)
        parties_joueurs = {}
        for r in resultats:
            key = r.get("partie_id") or f"{r['partie']}|{r['date']}"
            parties_joueurs.setdefault(key, set()).add(r["joueur"])

        # Trouver les keys correspondant exactement aux joueurs sélectionnés
        parties_trouvees = {k for k, joueurs_set in parties_joueurs.items() if joueurs_set == set(joueurs_selectionnes)}

        # Filtrer les résultats en gardant uniquement les entrées dont la party_key est dans parties_trouvees
        resultats_filtres = [r for r in resultats if (r.get("partie_id") or f"{r['partie']}|{r['date']}") in parties_trouvees]
    else:
        resultats_filtres = resultats

    # Recherche par nom ou date
    recherche_nom = st.text_input("Rechercher par nom de partie")
    recherche_date = st.date_input("Rechercher par date", value=None)

    # Filtrer les résultats en fonction des critères de recherche
    if recherche_nom:
        resultats_filtres = [r for r in resultats_filtres if recherche_nom.lower() in r["partie"].lower()]
    if recherche_date:
        resultats_filtres = [r for r in resultats_filtres if r["date"] == recherche_date.strftime("%Y-%m-%d")]

    # Trier les résultats par date (du plus récent au plus ancien)
    resultats_filtres.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)
    # Construire une table avec une ligne par partie
    # Regrouper par partie (partie_id si disponible, sinon 'partie|date')
    parties = {}
    for r in resultats_filtres:
        key = r.get("partie_id") or f"{r['partie']}|{r['date']}"
        if key not in parties:
            parties[key] = {
                "partie": r["partie"],
                "date": r["date"],
                "positions": {}
            }
        parties[key]["positions"][r["position"]] = r["joueur"]

    if parties:
        # Déterminer le nombre maximum de positions pour créer les colonnes
        max_pos = 0
        for p in parties.values():
            if p["positions"]:
                max_pos = max(max_pos, max(p["positions"].keys()))

        # Construire les lignes du tableau
        table_rows = []
        for key, p in parties.items():
            row = {
                "Nom du jeu": p["partie"],
                "Date": p["date"]
            }
            for pos in range(1, max_pos + 1):
                row[f"Position {pos}"] = p["positions"].get(pos, "")
            table_rows.append(row)

        # Afficher la table (DataFrame-like)
        import pandas as pd
        df = pd.DataFrame(table_rows)
        # Trier par date décroissante
        try:
            df["Date_sort"] = pd.to_datetime(df["Date"]) 
            df = df.sort_values(by="Date_sort", ascending=False).drop(columns=["Date_sort"])
        except Exception:
            pass

        st.table(df)
    else:
        st.write("Aucun résultat trouvé.")

# Page "Ajouter un joueur"
elif page == "Ajouter un joueur":
    if verifier_mot_de_passe():
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
    if verifier_mot_de_passe():
        st.title("Ajouter une Partie")

        # Formulaire pour ajouter une partie
        nom_jeu = st.text_input("Nom du jeu")
        date_partie = st.date_input("Date de la partie", datetime.today())
        nombre_joueurs = st.number_input("Nombre de joueurs", min_value=1, value=1)

        results = []
        for i in range(1, nombre_joueurs + 1):
            joueur = st.selectbox(f"Joueur à la position {i}", [""] + joueurs)
            if joueur:
                results.append({
                    "partie": nom_jeu,
                    "date": date_partie.strftime("%Y-%m-%d"),
                    "position": i,
                    "joueur": joueur
                })

        if st.button("Ajouter la partie"):
            if nom_jeu and all(result["joueur"] for result in results):
                # Générer un identifiant unique pour la partie
                id_partie = str(uuid.uuid4())
                # Ajouter l'identifiant à chaque résultat de la partie
                for r in results:
                    r["partie_id"] = id_partie
                # Enregistrer les résultats (plusieurs lignes: une par joueur/position)
                resultats.extend(results)
                sauvegarder_resultats(resultats)
                st.success("Partie ajoutée avec succès !")
            else:
                st.error("Veuillez remplir tous les champs.")
