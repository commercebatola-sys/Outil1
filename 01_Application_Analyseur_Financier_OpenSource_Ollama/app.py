import streamlit as st
import os
import fitz  # PyMuPDF
import ollama
import tempfile
from pathlib import Path
import json
from datetime import datetime
import pandas as pd

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Analyseur de Documents Financiers - Ollama",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour une interface moderne
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown("""
<div class="main-header">
    <h1>📊 Analyseur de Documents Financiers</h1>
    <p>Analysez vos rapports financiers avec Ollama Llama 3.1 et posez des questions interactives</p>
</div>
""", unsafe_allow_html=True)

# Configuration d'Ollama
def check_ollama_connection():
    """Vérifie la connexion à Ollama"""
    try:
        # Vérifier si Ollama est accessible
        models = ollama.list()
        return True, models
    except Exception as e:
        return False, str(e)

# Sidebar pour la configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Section Ollama
    with st.expander("🤖 Configuration Ollama", expanded=True):
        # Vérifier la connexion
        is_connected, models_info = check_ollama_connection()
        
        if is_connected:
            st.success("✅ Connexion Ollama établie")
            
            # Afficher les modèles disponibles
            if models_info and hasattr(models_info, 'models'):
                available_models = [model.model for model in models_info.models]
                st.info(f"📋 Modèles disponibles: {', '.join(available_models)}")
            else:
                st.warning("⚠️ Aucun modèle trouvé")
        else:
            st.error(f"❌ Erreur de connexion Ollama: {models_info}")
            st.info("Veuillez démarrer Ollama et télécharger le modèle Llama 3.1")
        
        # Sélection du modèle
        if models_info and hasattr(models_info, 'models') and models_info.models:
            available_models = [model.model for model in models_info.models]
            if available_models:
                model = st.selectbox(
                    "Modèle Ollama",
                    available_models,
                    index=0,
                    help="Choisissez le modèle Ollama à utiliser"
                )
            else:
                st.warning("⚠️ Aucun modèle disponible")
                model = None
        else:
            st.warning("⚠️ Impossible de récupérer la liste des modèles")
            model = None
    
    # Section paramètres
    with st.expander("📊 Paramètres d'analyse", expanded=True):
        max_length = st.slider(
            "Longueur maximale du texte (caractères)",
            min_value=50000,
            max_value=200000,
            value=120000,
            step=10000
        )
        
        summary_length = st.slider(
            "Longueur du résumé (mots)",
            min_value=150,
            max_value=500,
            value=300,
            step=50
        )
        
        temperature = st.slider(
            "Température (créativité)",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Plus la température est élevée, plus les réponses sont créatives"
        )

# Fonction pour extraire le texte du PDF
def extract_pdf_text(pdf_file, max_length=120000):
    """Extrait le texte d'un fichier PDF avec repères de pages"""
    try:
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name
        
        # Ouvrir le PDF
        pdf = fitz.open(tmp_path)
        text = ""
        
        for i, page in enumerate(pdf, start=1):
            page_text = page.get_text()
            text += f"\n\n=== [PAGE {i}] ===\n{page_text.strip()}"
        
        pdf.close()
        
        # Nettoyer le fichier temporaire
        os.unlink(tmp_path)
        
        # Nettoyer le texte
        text = "\n".join(line.strip() for line in text.splitlines())
        
        # Tronquer si nécessaire
        if len(text) > max_length:
            text = text[:max_length]
            st.warning(f"⚠️ Le texte a été tronqué à {max_length:,} caractères pour des raisons de performance.")
        
        return text
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du PDF: {str(e)}")
        return None

# Fonction pour générer le résumé avec Ollama
def generate_summary_ollama(text, model, summary_length=300, temperature=0.3):
    """Génère un résumé financier avec Ollama"""
    
    system_prompt = f"""Tu es analyste financier expert. On te fournit le texte d'un document financier
(rapport annuel, trimestriel, comptes, bilan, annexes).

Produis une synthèse **précise et chiffrée** en Markdown selon ce cadre :

- **Société / Période / Devise** : (si repérable)
- **Résumé exécutif** : activité, faits marquants, contexte ({summary_length//4}-{summary_length//3} lignes)
- **Chiffres clés** (tableau) :
 | Indicateur | Valeur | Évolution/Contexte | Période | Page |
 |---|---:|---|---|---:|
 (exemples : Chiffre d'affaires, EBIT/EBITDA, Résultat net, Marge, FCF, CAPEX,
 Dette nette, Trésorerie, etc.)
- **Analyse** :
 - Performance (croissance, marges, cash)
 - Structure financière (dette, liquidité)
 - Risques & incertitudes (marché, réglementation, change)
 - Outlook / Guidance (si communiqué)
- **Références internes** : pages/sections à relire

Exigences :
- **N'invente aucun chiffre**. Si une valeur n'apparaît pas clairement : `non précisé`.
- Cite la **Page** d'origine quand c'est possible (repère `=== [PAGE X] ===`).
- 6 à 12 **indicateurs quantitatifs** maximum (les plus utiles).
- Reste concis : {summary_length-50}-{summary_length+50} mots hors tableau."""

    try:
        # Appel à Ollama
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            options={
                "temperature": temperature,
                "num_predict": 2000
            }
        )
        
        return response['message']['content']
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la génération du résumé: {str(e)}")
        return None

# Fonction pour répondre aux questions avec Ollama
def answer_question_ollama(question, text, model, temperature=0.1):
    """Répond à une question spécifique sur le document avec Ollama"""
    
    system_prompt = """Tu es analyste financier. On te donne un extrait de rapport financier. 
Réponds uniquement à la question posée, sans inventer de données. 
Si la réponse n'est pas claire dans le texte, écris : 'non précisé'. 
Quand c'est possible, indique aussi la page d'origine (repère '=== [PAGE X] ===').
Sois concis et précis."""

    try:
        # Appel à Ollama
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question : {question}\n\nTexte PDF :\n{text}"}
            ],
            options={
                "temperature": temperature,
                "num_predict": 500
            }
        )
        
        return response['message']['content']
        
    except Exception as e:
        return f"❌ Erreur lors de la génération de la réponse: {str(e)}"

# Interface principale
ollama_status, models_info = check_ollama_connection()
if not ollama_status:
    st.error("⚠️ Impossible de se connecter à Ollama. Veuillez vérifier que le service est démarré.")
    st.info("""
    **Pour démarrer Ollama :**
    1. Installez Ollama depuis https://ollama.ai
    2. Lancez la commande : `ollama serve`
    3. Téléchargez le modèle : `ollama pull llama3.1:8b`
    """)
    st.stop()

# Vérifier qu'au moins un modèle est disponible
if not models_info or not hasattr(models_info, 'models') or not models_info.models:
    st.error("⚠️ Aucun modèle Ollama disponible.")
    st.info("""
    **Pour télécharger un modèle :**
    ```bash
    ollama pull llama3.1:8b
    ```
    """)
    st.stop()

# Section d'upload du PDF
st.markdown("## 📁 Import du Document")
uploaded_file = st.file_uploader(
    "Choisissez un fichier PDF financier",
    type=['pdf'],
    help="Formats acceptés: PDF uniquement"
)

if uploaded_file is not None:
    # Afficher les informations du fichier
    file_details = {
        "Nom du fichier": uploaded_file.name,
        "Taille": f"{uploaded_file.size / 1024 / 1024:.2f} MB",
        "Type": uploaded_file.type
    }
    
    col1, col2, col3 = st.columns(3)
    for key, value in file_details.items():
        with col1 if key == "Nom du fichier" else col2 if key == "Taille" else col3:
            st.metric(key, value)
    
    # Bouton pour analyser le PDF
    if st.button("🔍 Analyser le Document", type="primary"):
        with st.spinner("📖 Extraction du texte en cours..."):
            text = extract_pdf_text(uploaded_file, max_length)
        
        if text:
            st.success("✅ Texte extrait avec succès!")
            
            # Aperçu du texte
            with st.expander("👀 Aperçu du texte extrait", expanded=False):
                st.text_area("Texte extrait", text[:2000] + "..." if len(text) > 2000 else text, height=200)
            
            # Génération du résumé
            with st.spinner("🤖 Génération du résumé en cours..."):
                summary = generate_summary_ollama(text, model, summary_length, temperature)
            
            if summary:
                st.markdown("## 📊 Résumé Financier")
                st.markdown(summary)
                
                # Sauvegarder le contexte pour les questions
                st.session_state['pdf_text'] = text
                st.session_state['summary'] = summary
                
                # Bouton de téléchargement du résumé
                st.download_button(
                    label="💾 Télécharger le Résumé",
                    data=summary,
                    file_name=f"resume_financier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )

# Section des questions interactives
if 'pdf_text' in st.session_state:
    st.markdown("## 💬 Questions Interactives")
    st.markdown("Posez des questions spécifiques sur votre document financier")
    
    # Interface de chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Affichage de l'historique des conversations
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>Vous :</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant :</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
    
    # Interface de saisie de question
    col1, col2 = st.columns([4, 1])
    with col1:
        question = st.text_input(
            "Posez votre question",
            placeholder="Ex: Quel est le chiffre d'affaires ? Quelle est la marge nette ?",
            key="question_input"
        )
    
    with col2:
        if st.button("❓ Poser", type="primary"):
            if question.strip():
                # Ajouter la question à l'historique
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': question
                })
                
                # Générer la réponse
                with st.spinner("🤔 Recherche en cours..."):
                    answer = answer_question_ollama(
                        question, 
                        st.session_state['pdf_text'], 
                        model, 
                        temperature
                    )
                
                # Ajouter la réponse à l'historique
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': answer
                })
                
                # Recharger la page pour afficher la nouvelle conversation
                st.rerun()
    
    # Bouton pour effacer l'historique
    if st.session_state.chat_history:
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.chat_history = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>📊 Analyseur de Documents Financiers - Propulsé par Ollama Llama 3.1</p>
    <p><small>Développé pour l'analyse automatisée de rapports financiers</small></p>
</div>
""", unsafe_allow_html=True)
