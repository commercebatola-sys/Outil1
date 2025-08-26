# 📊 Analyseur de Documents Financiers - OpenRouter

Une application Streamlit moderne qui analyse vos documents PDF financiers avec l'intelligence artificielle via OpenRouter (accès à multiples modèles).

## ✨ Fonctionnalités

- **📁 Upload de PDF** : Téléchargez vos rapports financiers (annuels, trimestriels, bilans, etc.)
- **🤖 Analyse IA** : Génération automatique de résumés structurés avec OpenRouter
- **📊 Résumé structuré** : 
  - Société, période et devise
  - Résumé exécutif
  - Chiffres clés dans un tableau
  - Analyse détaillée
  - Références aux pages
- **❓ Questions interactives** : Posez des questions spécifiques sur votre document
- **💾 Export** : Téléchargez le résumé au format Markdown
- **🎨 Interface moderne** : Design responsive et intuitif

## 🚀 Installation

### 1. Prérequis

- Python 3.8+
- Compte OpenRouter avec clé API

### 2. Création de l'Environnement Virtuel

#### Méthode 1 : venv (Recommandée)
```bash
# Créer l'environnement virtuel
python -m venv openrouter_env

# Activer l'environnement
# Sur macOS/Linux :
source openrouter_env/bin/activate
# Sur Windows :
openrouter_env\Scripts\activate

# Vérifier l'activation
which python  # macOS/Linux
where python  # Windows
```

#### Méthode 2 : Conda
```bash
# Créer l'environnement conda
conda create -n openrouter_env python=3.11

# Activer l'environnement
conda activate openrouter_env

# Vérifier l'activation
conda info --envs
```

#### Méthode 3 : Poetry
```bash
# Installer Poetry si pas déjà fait
curl -sSL https://install.python-poetry.org | python3 -

# Créer et activer l'environnement
poetry install
poetry shell
```

### 3. Cloner le projet
```bash
git clone <votre-repo>
cd 02_Application_Analyseur_Financier_OpenSource_OpenRouter
```

### 4. Installer les dépendances
```bash
# S'assurer que l'environnement virtuel est activé
# L'invite de commande doit commencer par (openrouter_env)

pip install -r requirements.txt

# Vérifier l'installation
pip list
```

### 5. Configuration de l'API OpenRouter
Créer un fichier `.env` à la racine du projet :
```env
OPENROUTER_API_KEY=votre_cle_api_openrouter_ici
```

**Comment obtenir votre clé API :**
1. Allez sur [openrouter.ai](https://openrouter.ai)
2. Créez un compte ou connectez-vous
3. Allez dans "API Keys"
4. Créez une nouvelle clé API
5. Copiez la clé dans votre fichier `.env`

### 6. Vérifier l'installation
```bash
# Tester Python
python --version

# Tester Streamlit
streamlit --version

# Tester les variables d'environnement
python -c "import os; print('API Key:', os.getenv('OPENROUTER_API_KEY')[:10] + '...' if os.getenv('OPENROUTER_API_KEY') else 'Non trouvée')"
```

### 7. Lancer l'application
```bash
# S'assurer que l'environnement virtuel est activé
source openrouter_env/bin/activate  # macOS/Linux
# ou
conda activate openrouter_env        # Conda

streamlit run app.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

## 🔧 Configuration

### Modèles OpenRouter disponibles
- **GPT-4o** (recommandé) : Analyse la plus précise et détaillée
- **GPT-4 Turbo** : Bon équilibre performance/coût
- **GPT-3.5 Turbo** : Plus rapide, moins coûteux
- **Claude 3.5 Sonnet** : Alternative performante
- **Llama 3.1 70B** : Modèle open source de qualité

### Paramètres ajustables
- **Longueur maximale du texte** : Contrôle la taille des documents analysés (50k à 200k caractères)
- **Temperature** : Contrôle la créativité des réponses (fixée à 0.3 pour la précision)

## 📖 Utilisation

### 1. Téléchargement du document
- Cliquez sur "Choisir un fichier" dans la section de téléchargement
- Sélectionnez votre PDF financier
- L'application analysera automatiquement le document

### 2. Génération du résumé
- Cliquez sur "🚀 Générer le Résumé Financier"
- Attendez que l'IA analyse votre document
- Le résumé structuré s'affichera avec :
  - Métriques clés
  - Tableau des indicateurs financiers
  - Analyse détaillée
  - Références aux pages

### 3. Questions interactives
- Utilisez la section chat en bas de page
- Posez des questions spécifiques sur votre document
- L'IA répondra en se basant uniquement sur le contenu du PDF
- L'historique des questions est conservé pendant la session

### 4. Export du résumé
- Cliquez sur "💾 Télécharger le Résumé"
- Le fichier sera téléchargé au format Markdown

## 🎯 Exemples de questions

- "Quel est le chiffre d'affaires 2023 ?"
- "Quelle est la marge nette du groupe ?"
- "Quels sont les principaux risques identifiés ?"
- "Quelle est la dette nette ?"
- "Quelles sont les perspectives de croissance ?"

## 🔒 Sécurité et confidentialité

- **Aucun stockage** : Vos documents ne sont pas sauvegardés sur nos serveurs
- **Traitement temporaire** : Les fichiers sont traités en mémoire et supprimés après analyse
- **API sécurisée** : Communication chiffrée avec OpenRouter
- **Variables d'environnement** : Vos clés API restent locales

## 🛠️ Structure du code

```
02_Application_Analyseur_Financier_OpenSource_OpenRouter/
├── app.py                 # Application principale Streamlit
├── requirements.txt       # Dépendances Python
├── README.md             # Documentation
├── .env                  # Configuration API (à créer)
├── data/                 # Dossier pour vos documents PDF
│   └── teslafinancialreport.pdf  # Document d'exemple
└── .streamlit/           # Configuration Streamlit
    └── config.toml
```

## 📝 Format de sortie

Le résumé généré suit une structure standardisée :

```markdown
# Synthèse Financière

- **Société / Période / Devise** : [Informations identifiées]

## Résumé Exécutif
[5-8 lignes de synthèse]

## Chiffres Clés
| Indicateur | Valeur | Évolution/Contexte | Période | Page |
|------------|---------|-------------------|---------|------|
[Tableau des métriques]

## Analyse
- Performance (croissance, marges, cash)
- Structure financière (dette, liquidité)
- Risques & incertitudes
- Outlook / Guidance

## Références internes
[Pages et sections importantes]
```

## 🚀 Workflow de Développement

### 1. Première utilisation
```bash
# Cloner le projet
git clone <votre-repo>
cd 02_Application_Analyseur_Financier_OpenSource_OpenRouter

# Créer l'environnement virtuel
python -m venv openrouter_env
source openrouter_env/bin/activate  # macOS/Linux

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'API OpenRouter
# (voir section configuration ci-dessus)

# Lancer l'application
streamlit run app.py
```

### 2. Utilisation quotidienne
```bash
# Activer l'environnement
source openrouter_env/bin/activate

# Lancer l'application
streamlit run app.py
```

### 3. Mise à jour des dépendances
```bash
# Activer l'environnement
source openrouter_env/bin/activate

# Mettre à jour
pip install --upgrade -r requirements.txt
```

## 🚨 Bonnes pratiques

1. **Vérifiez toujours** les chiffres affichés avec le document original
2. **Utilisez les références de pages** pour localiser les informations
3. **Posez des questions précises** pour obtenir des réponses détaillées
4. **Vérifiez la qualité** du PDF (texte lisible, pas d'images uniquement)
5. **Surveillez votre consommation** d'API OpenRouter

## 🐛 Résolution de problèmes

### Erreur de clé API
```bash
# Vérifier que votre fichier .env contient OPENROUTER_API_KEY=votre_cle
# Assurez-vous que la clé est valide et a des crédits

# Tester la clé
python -c "import os; print('API Key:', os.getenv('OPENROUTER_API_KEY')[:10] + '...' if os.getenv('OPENROUTER_API_KEY') else 'Non trouvée')"
```

### Erreur de lecture PDF
- Vérifiez que le PDF n'est pas protégé par mot de passe
- Assurez-vous que le PDF contient du texte (pas uniquement des images)
- Essayez avec un PDF plus simple pour tester

### Réponses imprécises
- Augmentez la longueur maximale du texte dans les paramètres
- Utilisez un modèle plus avancé (GPT-4o)
- Posez des questions plus spécifiques

### Problèmes d'environnement virtuel
```bash
# Si l'environnement ne s'active pas
deactivate  # Désactiver tout environnement actif
source openrouter_env/bin/activate  # Réactiver

# Si les packages ne sont pas trouvés
pip install --upgrade pip
pip install -r requirements.txt

# Vérifier le chemin Python
which python
pip show streamlit
```

## 💰 Coûts et Quotas

### Modèles et coûts (approximatifs)
- **GPT-3.5 Turbo** : ~$0.0015/1K tokens
- **GPT-4 Turbo** : ~$0.01/1K tokens (input), ~$0.03/1K tokens (output)
- **GPT-4o** : ~$0.005/1K tokens (input), ~$0.015/1K tokens (output)
- **Claude 3.5 Sonnet** : ~$0.003/1K tokens (input), ~$0.015/1K tokens (output)

### Estimation des coûts
- **Document de 50 pages** : ~$0.50 - $2.00 par analyse
- **Questions supplémentaires** : ~$0.10 - $0.50 par question
- **Usage intensif** : Considérez un plan payant OpenRouter

## 📞 Support

Pour toute question ou problème :
1. Vérifiez la documentation OpenRouter
2. Consultez les logs Streamlit dans le terminal
3. Vérifiez que toutes les dépendances sont installées
4. Vérifiez que votre environnement virtuel est activé

## 🔄 Mises à jour

L'application est régulièrement mise à jour pour :
- Améliorer la précision des analyses
- Ajouter de nouveaux modèles OpenRouter
- Optimiser les performances
- Améliorer l'interface utilisateur

## 🔗 Liens Utiles

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter API Keys](https://openrouter.ai/keys)
- [Documentation Streamlit](https://docs.streamlit.io/)
- [Modèles disponibles](https://openrouter.ai/models)

---

**⚡ Propulsé par OpenRouter et Streamlit**

**💡 Avantage principal** : Accès à multiples modèles d'IA, performance optimale, coût contrôlé !
