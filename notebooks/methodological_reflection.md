# Réflexion Méthodologique : Prédiction de la Réussite Scolaire

Ce document synthétise le cheminement intellectuel et technique qui a conduit aux résultats finaux du projet. Il explicite les choix stratégiques, les hypothèses posées et les leçons tirées des expérimentations.

## 1. Analyse du Besoin et Cadrage

Dès la lecture du sujet, deux approches se distinguaient pour prédire la note finale `G3` :

1.  **Approche "Performance Pure"** : Chercher à obtenir le meilleur score R2 possible.
2.  **Approche "Utilité Pédagogique"** : Chercher à identifier les élèves en difficulté le plus tôt possible.

**Décision** : Ne pas choisir, mais **comparer**. J'ai structuré l'analyse autour de deux scénarios contrastés pour démontrer la profondeur de la problématique.

## 2. Définition des Scénarios

C'est le cœur de la stratégie de modélisation.

- **Scénario 1 : Prédiction Finale ("Late Prediction")**
  - _Variables_ : Toutes, incluant les notes trimestrielles `G1` et `G2`.
  - _Hypothèse_ : Ce modèle sera très performant mais peu utile pour l'intervention précoce, car `G1` et `G2` sont connus tardivement et sont fortement corrélés à `G3`.
- **Scénario 2 : Prédiction Précoce ("Early Prediction")**
  - _Variables_ : Uniquement les données socio-démographiques (famille, temps d'étude, santé...), sans aucune note.
  - _Hypothèse_ : Ce modèle sera moins performant mais crucial pour détecter les profils à risque dès la rentrée scolaire.

## 3. Choix Techniques et Architecture

- **Séparation des Notebooks** : J'ai choisi de séparer le code technique (`main_analysis.ipynb`) du journal de bord (`journal.ipynb`). Cela permet de garder une trace narrative claire (pour l'humain) distincte de l'exécution du code (pour la machine).
- **Modélisation** :
  - _Régression Linéaire_ : Pour établir une "baseline" simple et interprétable.
  - _Random Forest_ : Choisi pour sa capacité à gérer des relations non-linéaires et des interactions complexes entre variables catégorielles sans nécessiter un feature engineering lourd.

## 4. Itérations et Apprentissages

Le processus n'a pas été linéaire. Voici comment les résultats intermédiaires ont orienté la réflexion :

### A. Le Constat d'Échec du Scénario "Précoce"

Les premiers résultats ont montré un gouffre entre les deux scénarios :

- Scénario Final : R2 > 0.80 (Excellent)
- Scénario Précoce : R2 ~ 0.25 (Médiocre)

**Interprétation** : Les données démographiques seules expliquent très peu la variance de la note finale. Un élève avec un contexte difficile peut très bien réussir, et inversement.

### B. Tentative d'Amélioration par le Feature Engineering

**Hypothèse** : "Peut-être que l'information est dissolue entre trop de variables."
**Action** : Création de variables agrégées :

- `TotalAlc` = Somme de la consommation d'alcool semaine/weekend. _(Choix validé par la forte corrélation de 0.65 entre Dalc et Walc et leur cœfficient de corrélation identique avec la note finale)._
- `ParentEdu` = Somme de l'éducation père/mère.
  **Résultat** : Gain très marginal. Ce n'est pas la _forme_ des données qui limite, mais le _contenu_.

### C. Tentative d'Amélioration par le Volume de Données

**Hypothèse** : "Le modèle manque d'exemples pour généraliser (seulement 395 élèves en Math)."
**Action** : Fusion des datasets Math et Portugais (N=1044) en traitant la matière comme une variable (`Subject`).
**Résultat** : R2 stagne autour de 0.24.
**Conclusion Définitive** : Ce n'est pas un problème de taille d'échantillon. C'est une limite intrinsèque : **le passé scolaire (les notes) reste le seul prédicteur fiable de l'avenir scolaire.**

## 5. Processus de Sélection des Modèles (Audit)

Suite à une demande de validation rigoureuse des choix de modélisation, j'ai mis en place un protocole de benchmark (disponible dans `notebooks/model_benchmarking.ipynb`) comparant 5 modèles sur 5 plis de validation croisée.

### Résultats du Benchmark

| Scénario  | Modèle                 | R2 (Score) | RMSE     | Commentaire                                                                         |
| --------- | ---------------------- | ---------- | -------- | ----------------------------------------------------------------------------------- |
| **Early** | **SVR**                | **0.165**  | 3.36     | Meilleure performance mais temps d'entrainement élevé sur gros volumes.             |
| Early     | Random Forest          | 0.113      | 3.33     | Décevant sur ce scénario très bruité.                                               |
| Early     | Linear Regression      | 0.023      | 3.58     | Incapable de capturer la complexité non-linéaire.                                   |
| Early     | LightGBM               | 0.010      | 3.50     | Très mauvais ici (overfitting probable sur bruit).                                  |
| **Late**  | **Ensemble (LR + RF)** | **0.795**  | **1.59** | **Meilleur Absolu**. Combine la stabilité de la régression et la flexibilité du RF. |
| Late      | Linear Regression      | 0.784      | 1.65     | Excellent baseline.                                                                 |
| Late      | Random Forest          | 0.775      | 1.65     | Excellent mais moins interprétable que la régression.                               |
| Late      | LightGBM               | 0.753      | 1.73     | Bon mais sans avantage décisif.                                                     |

### Justification des Choix

1.  **Abandon des Réseaux de Neurones (MLP)** : Les tests ont montré des problèmes de convergence et une performance médiocre (R2 négatif parfois), dus à la trop petite taille du dataset pour le Deep Learning.
2.  **Sélection pour le Scénario Final** : L'approche hybride (**Voting Regressor : Linear + Random Forest**) a démontré la meilleure performance (R2 ~ 0.80). Elle permet de lisser les prédictions et de réduire la variance du Random Forest tout en gardant la tendance linéaire forte imposée par les notes G1/G2. C'est le choix retenu pour la production.
3.  **Sélection pour le Scénario Précoce** : Bien que le **SVR** soit techniquement meilleur, le score reste trop faible (0.16) pour être utilisable. Nous maintenons la conclusion que ce scénario doit être réorienté vers de la _détection_ (Classification) plutôt que de la _prédiction_ (Régression), où les méthodes par ensembles (RF) sont souvent plus maniables pour extraire l'importance des variables.

## 5. Synthèse pour le Rendu

Face à ces constats, ma recommandation finale pour la soutenance a évolué : ne pas vendre le modèle "Précoce" comme un outil de prédiction de note (car il se trompe trop), mais le repositionner comme un **outil de détection de risque** (binaire).

## 6. Dimension Éthique et Usage des Données Sensibles

L'utilisation de ce jeu de données soulève des questions éthiques majeures sur la collecte et l'exploitation de données personnelles dans un contexte éducatif.

### A. Nature des Données Sensibles

Le dataset contient des informations qui relèvent de la sphère privée, voire intime :

- **Situation Familiale** : `Pstatus` (cohabitation des parents), `famrel` (qualité des relations familiales).
- **Santé et Comportement** : `Dalc`/`Walc` (consommation d'alcool), `health` (état de santé).
- **Origine Sociale** : `Medu`/`Fedu` et `Mjob`/`Fjob` (niveau d'étude et emploi des parents).

### B. Risques de Biais et de Stigmatisation

L'utilisation de ces variables dans un modèle prédictif ("Early Prediction") présente un risque de **prophétie auto-réalisatrice**. Si un modèle prédit l'échec d'un élève uniquement parce que ses parents sont séparés ou peu diplômés :

1.  L'équipe pédagogique pourrait inconsciemment moins investir sur cet élève.
2.  Cela renforce le déterminisme social au lieu de le combattre.

### C. Recommandations pour un Usage Responsable

- **Principe de Minimisation** : Avons-nous vraiment besoin de connaître la consommation d'alcool pour aider un élève ? Si l'impact sur le modèle est marginal (ce que nos tests ont montré avec R2 ~ 0.25), ces données devraient être **exclues** par précaution pour protéger la vie privée.
- **Transparence** : L'élève et sa famille doivent savoir sur quels critères ils sont évalués. Un score de "risque" basé sur des critères opaques ou sociaux est éthiquement contestable.
- **Finalité** : L'IA ne doit pas servir à filtrer ou sélectionner, mais uniquement à déclencher des dispositifs de soutien humain.

Cette démarche réflexive — poser des hypothèses, tester, échouer, et réajuster l'interprétation métier — constitue la véritable valeur ajoutée de ce travail, au-delà du simple code.
