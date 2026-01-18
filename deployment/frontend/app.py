
import streamlit as st
import requests
import json
import pandas as pd
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Portail Simplon", page_icon="🎓", layout="wide")

# Sidebar Navigation
with st.sidebar:
    page = option_menu(
        "Navigation", 
        ["Accueil", "Prédictions", "Administration"],
        icons=['house', 'calculator', 'gear'],
        menu_icon="cast", 
        default_index=0,
    )

if page == "Accueil":
    st.title("🏠 Portail des Services")
    st.markdown("### Bienvenue sur la plateforme de suivi et de prédiction.")
    st.markdown("Ce portail centralise l'accès aux différents services du projet.")

    c1, c2 = st.columns(2)
    
    with c1:
        st.info("**🤖 Application de Prédiction**\n\nEstimez la réussite future d'un étudiant en fonction de ses données académiques et personnelles.\n\n👉 *Utilisez l'onglet 'Prédictions' dans le menu latéral.*")
        
        st.warning("**📊 Monitoring Grafana**\n\nVisualisez les métriques de performance, les logs et l'état du système en temps réel.\n\n[Accéder à Grafana](https://simplon-grafana.dev.brad.team)")

    with c2:
        st.success("**📖 Documentation API**\n\nExplorez les endpoints de l'API, testez les requêtes et consultez les schémas de données via Swagger UI.\n\n[Accéder à la Doc API](https://simplon-api.dev.brad.team/docs)")
        
        st.error("**📈 Métriques Prometheus**\n\nAccès direct aux métriques brutes collectées par Prometheus.\n\n[Accéder à Prometheus](https://simplon-prometheus.dev.brad.team)")

    st.markdown("---")
    
    st.info("**🧪 Experiment Tracking**\n\nSuivi des expériences, des modèles et des paramètres via MLFlow.\n\n[Accéder à MLFlow](https://simplon-mlflow.dev.brad.team)")

    st.success("**🚀 Workflow Orchestration**\n\nGestion et planification des flux de données et de ré-entraînement avec Prefect.\n\n[Accéder à Prefect](https://simplon-prefect.dev.brad.team)")

    st.markdown("---")
    st.caption("🚀 M5_3 Project | Déployé avec Podman Compose")

elif page == "Prédictions":
    st.title("🎓 Calculateur de Réussite Étudiante")
    st.markdown("Entrez les informations académiques pour prédire la note finale (G3) sur 20.")

    with st.form("prediction_form"):
        st.subheader("Performance Académique (Priorité Haute)")
        col1, col2 = st.columns(2)
        
        with col1:
            G1 = st.slider("Note Premier Trimestre (0-20)", 0, 20, 10)
            G2 = st.slider("Note Second Trimestre (0-20)", 0, 20, 10)
            
        with col2:
            failures = st.slider("Nombre d'échecs passés", 0, 4, 0)
            absences = st.slider("Nombre d'absences", 0, 93, 2)
            studytime = st.select_slider("Temps d'étude hebdomadaire", options=[1, 2, 3, 4], value=2, format_func=lambda x: {1: "< 2h", 2: "2 à 5h", 3: "5 à 10h", 4: "> 10h"}[x])

        st.markdown("---")
        st.subheader("Environnement & Habitudes")
        col3, col4 = st.columns(2)
        
        with col3:
            schoolsup = st.selectbox("Soutien scolaire de l'établissement", ["non", "oui"])
            famsup = st.selectbox("Soutien scolaire familial", ["non", "oui"])
            paid = st.selectbox("Cours particuliers payants", ["non", "oui"])
            internet = st.selectbox("Accès Internet à la maison", ["non", "oui"])
            higher = st.selectbox("Veut faire des études supérieures", ["oui", "non"])

        with col4:
            activities = st.selectbox("Activités extra-scolaires", ["non", "oui"])
            freetime = st.slider("Temps libre (après l'école)", 1, 5, 3)
            goout = st.slider("Sorties entre amis", 1, 5, 3)
            traveltime = st.select_slider("Temps de trajet (maison-école)", options=[1, 2, 3, 4], value=1, format_func=lambda x: {1: "< 15 min", 2: "15 à 30 min", 3: "30 min à 1h", 4: "> 1h"}[x])

        # Hidden fields (Hardcoded defaults for ethical/privacy reasons)
        
        submitted = st.form_submit_button("Lancer la Prédiction")

    if submitted:
        # Mapping translations back to model values
        def map_yn(val):
            return "yes" if val == "oui" else "no"

        data = {
            # Hardcoded Default Values (Neutral/Median)
            "school": "GP", "sex": "F", "age": 17, "address": "U",
            "famsize": "GT3", "Pstatus": "T", "Medu": 2, "Fedu": 2,
            "Mjob": "other", "Fjob": "other", "reason": "course", "guardian": "mother",
            "nursery": "yes", "romantic": "no", "famrel": 4,
            "Dalc": 1, "Walc": 1, "health": 4,
            
            # User Inputs
            "G1": G1, "G2": G2, "failures": failures, "absences": absences,
            "studytime": studytime, "schoolsup": map_yn(schoolsup), 
            "famsup": map_yn(famsup), "paid": map_yn(paid),
            "activities": map_yn(activities), "higher": map_yn(higher), 
            "internet": map_yn(internet), "freetime": freetime, 
            "goout": map_yn(goout) if isinstance(goout, str) else goout, # Fix if goout was slider (int) or select (str). It's slider in UI (int), but mapped safely.
            "traveltime": traveltime
        }
        # Note: goout is a slider (1-5), so it returns int. No need to map_yn unless I changed it. 
        # In my code above: goout = st.slider... so it is int.
        # Wait, in data dict I see: "goout": goout. 
        # Check carefully: `map_yn(goout) if isinstance(goout, str) else goout` - safe.

        try:
            response = requests.post("http://api:8000/predict", json=data)
            if response.status_code == 200:
                pred = response.json()["prediction_G3"]
                st.success(f"Note Finale Prédite (G3) : {pred:.2f} / 20")
                
                if pred < 10:
                    st.error("⚠️ Risque d'échec détecté !")
                else:
                    st.balloons()
                    st.info("Performance satisfaisante attendue.")
            else:
                st.error(f"Erreur API : {response.text}")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")

elif page == "Administration":
    st.title("⚙️ Administration du Système")
    st.markdown("Gestion du cycle de vie des modèles et maintenance.")

    st.subheader("🔄 Ré-entraînement du Modèle")
    st.info("Cette action déclenchera un flux Prefect pour ré-entraîner le modèle avec les dernières données disponibles. Le nouveau modèle sera versionné automatiquement.")
    
    if st.button("Lancer le Ré-entraînement"):
        try:
            with st.spinner("Déclenchement du flux..."):
                response = requests.post("http://api:8000/retrain")
                if response.status_code == 200:
                    st.success("✅ Flux de ré-entraînement démarré avec succès !")
                    st.json(response.json())
                    st.markdown(f"[Suivre l'avancement sur Prefect](https://simplon-prefect.dev.brad.team)")
                else:
                    st.error(f"Erreur lors du déclenchement : {response.text}")
        except Exception as e:
            st.error(f"Erreur de connexion à l'API : {e}")
