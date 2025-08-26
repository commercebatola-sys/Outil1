import streamlit as st
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
import requests
import tempfile
import uuid

# Configuration de la page
st.set_page_config(
    page_title="Analyseur de Documents Financiers",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<h1 class="main-header">📊 Analyseur de Documents Financiers</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Analysez vos rapports financiers avec l\'intelligence artificielle via OpenRouter</p>', unsafe_allow_html=True)

# Sidebar pour la configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Chargement des variables d'environnement
    load_dotenv()
    api_key_env = os.getenv("OPENROUTER_API_KEY")
    
    # Section pour la clé API
    st.markdown("### 🔑 Clé API OpenRouter")
    
    if api_key_env:
        st.success("✅ Clé API OpenRouter trouvée dans le fichier .env")
        use_env_key = st.checkbox("Utiliser la clé du fichier .env", value=True)
        if use_env_key:
            api_key = api_key_env
        else:
            api_key = st.text_input("Ou entrez une autre clé API:", type="password", key="custom_api_key")
    else:
        st.warning("⚠️ Aucune clé API OpenRouter trouvée dans le fichier .env")
        st.info("""
        Pour configurer votre clé API OpenRouter, vous avez 2 options :
        
        **Option 1 (Recommandée) :** Créez un fichier `.env` dans ce dossier avec :
        ```
        OPENROUTER_API_KEY=votre_cle_api_ici
        ```
        
        **Option 2 :** Entrez votre clé directement ci-dessous :
        """)
        api_key = st.text_input("Entrez votre clé API OpenRouter:", type="password", key="manual_api_key")
        
        if api_key:
            st.success("✅ Clé API saisie !")
        else:
            st.error("❌ Clé API requise pour utiliser l'application")
    
    # Validation de la clé API
    if api_key and len(api_key) < 20:
        st.error("❌ La clé API semble incorrecte (trop courte)")
        api_key = None
    
    # Sélection du modèle
    model = st.selectbox(
        "Modèle OpenRouter:",
        ["mistralai/mistral-7b-instruct", "meta-llama/llama-3.1-8b-instruct", "anthropic/claude-3-haiku"],
        index=0
    )
    
    # Paramètres
    st.markdown("### 📋 Paramètres")
    max_length = st.slider("Longueur maximale du texte (caractères):", 50000, 200000, 120000, step=10000)
    
    st.markdown("---")
    st.markdown("### 📚 À propos")
    st.info("""
    Cette application analyse vos documents PDF financiers et génère :
    - Un résumé exécutif structuré
    - Les chiffres clés
    - Une analyse détaillée
    - Réponses à vos questions spécifiques
    
    **🔐 Sécurité :** Vos données restent privées et ne sont pas stockées.
    **🌐 API :** Utilise OpenRouter pour accéder à différents modèles d'IA.
    """)
    
    if not api_key:
        st.markdown("### ⚠️ Action requise")
        st.error("""
        **L'application nécessite une clé API OpenRouter pour fonctionner.**
        
        🔑 Obtenez votre clé API sur : https://openrouter.ai/keys
        
        📝 Puis configurez-la en utilisant une des options ci-dessus.
        """)

# Fonction pour extraire le texte du PDF
def extract_pdf_text(pdf_file, max_length):
    try:
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name
        
        # Ouvrir le PDF avec PyMuPDF
        pdf = fitz.open(tmp_path)
        texte = ""
        
        for i, page in enumerate(pdf, start=1):
            texte_page = pdf[i-1].get_text()
            texte += f"\n\n=== [PAGE {i}] ===\n" + texte_page.strip()
        
        pdf.close()
        
        # Nettoyer le texte
        texte = "\n".join(l.strip() for l in texte.splitlines())
        
        # Tronquer si nécessaire
        if len(texte) > max_length:
            texte = texte[:max_length]
            st.warning(f"⚠️ Le texte a été tronqué à {max_length} caractères pour des raisons de performance.")
        
        # Nettoyer le fichier temporaire
        os.unlink(tmp_path)
        
        return texte
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF: {str(e)}")
        return None

# Fonction pour générer le résumé via OpenRouter
def generate_summary(text, api_key, model):
    try:
        # Configuration pour OpenRouter
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:8888/",
            "Content-Type": "application/json"
        }
        
        # URL de l'API OpenRouter
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        consignes = (
            "Tu es analyste financier. On te fournit le texte d'un document financier\n"
            "(rapport annuel, trimestriel, comptes, bilan, annexes).\n\n"
            "Produis une synthèse **précise et chiffrée** en Markdown selon ce cadre :\n\n"
            "- **Société / Période / Devise** : (si repérable)\n"
            "- **Résumé exécutif (5–8 lignes)** : activité, faits marquants, contexte\n"
            "- **Chiffres clés** (tableau) :\n"
            " | Indicateur | Valeur | Évolution/Contexte | Période | Page |\n"
            " |---|---:|---|---|---:|\n"
            " (exemples : Chiffre d'affaires, EBIT/EBITDA, Résultat net, Marge, FCF, CAPEX,\n"
            " Dette nette, Trésorerie, NPL/Coût du risque pour banque, CET1, LCR/NSFR, etc.)\n"
            "- **Analyse** :\n"
            " - Performance (croissance, marges, cash)\n"
            " - Structure financière (dette, liquidité)\n"
            " - Risques & incertitudes (marché, réglementation, change)\n"
            " - Outlook / Guidance (si communiqué)\n"
            "- **Références internes** : pages/sections à relire\n\n"
            "Exigences :\n"
            "- **N'invente aucun chiffre**. Si une valeur n'apparaît pas clairement : `non précisé`.\n"
            "- Cite la **Page** d'origine quand c'est possible (repère `=== [PAGE X] ===`).\n"
            "- 6 à 12 **indicateurs quantitatifs** maximum (les plus utiles).\n"
            "- Reste concis : 200–350 mots hors tableau."
        )
        
        # Préparation de la requête
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": consignes},
                {"role": "user", "content": text}
            ]
        }
        
        # Appel API
        response = requests.post(api_url, json=payload, headers=headers)
        response_json = response.json()
        
        # Extraction du texte de la réponse
        return response_json['choices'][0]['message']['content']
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du résumé: {str(e)}")
        return None

# Fonction pour répondre aux questions via OpenRouter
def answer_question(question, text, api_key, model):
    try:
        # Configuration pour OpenRouter
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:8888/",
            "Content-Type": "application/json"
        }
        
        # URL de l'API OpenRouter
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        consignes_questions = (
            "Tu es analyste financier. On te donne le texte d'un rapport financier. "
            "Réponds uniquement à la question posée, sans inventer de données. "
            "Si la réponse n'est pas claire dans le texte, écris : 'non précisé'. "
            "Quand c'est possible, indique aussi la page d'origine (repère '=== [PAGE X] ===')."
        )
        
        # Préparation de la requête
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": consignes_questions},
                {"role": "user", "content": f"Question : {question}\n\nTexte PDF :\n{text}"}
            ]
        }
        
        # Appel API
        response = requests.post(api_url, json=payload, headers=headers)
        response_json = response.json()
        
        # Extraction du texte de la réponse
        return response_json['choices'][0]['message']['content']
        
    except Exception as e:
        st.error(f"Erreur lors de la réponse à la question: {str(e)}")
        return None

# Interface principale
if not api_key:
    st.markdown('<h2 class="sub-header">🚫 Configuration requise</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.error("""
        ### ⚠️ Clé API OpenRouter requise
        
        L'application ne peut pas fonctionner sans une clé API OpenRouter valide.
        """)
        
        st.info("""
        **Comment obtenir votre clé API :**
        
        1. 🌐 Rendez-vous sur https://openrouter.ai/keys
        2. 🔐 Connectez-vous ou créez un compte OpenRouter
        3. ➕ Cliquez sur "Create API Key"
        4. 📋 Copiez la clé générée
        5. 🔧 Configurez-la dans la sidebar ←
        """)
        
        st.warning("""
        **💰 Note importante :** L'utilisation de l'API OpenRouter peut être payante selon le modèle choisi. 
        Consultez les tarifs sur https://openrouter.ai/pricing
        """)
    
    st.stop()

# Section de téléchargement du PDF
st.markdown('<h2 class="sub-header">📁 Téléchargement du Document</h2>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choisissez votre document PDF financier",
    type=['pdf'],
    help="Formats acceptés: PDF uniquement"
)

# Variables de session
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Traitement du PDF
if uploaded_file is not None:
    with st.spinner("📖 Analyse du document en cours..."):
        pdf_text = extract_pdf_text(uploaded_file, max_length)
        
        if pdf_text:
            st.session_state.pdf_text = pdf_text
            
            # Aperçu du texte
            with st.expander("👁️ Aperçu du document (cliquez pour voir)"):
                st.text(pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text)
            
            st.success(f"✅ Document analysé avec succès ! ({len(pdf_text)} caractères)")
            
            # Bouton pour générer le résumé
            if st.button("🚀 Générer le Résumé Financier", use_container_width=True):
                with st.spinner("🤖 Génération du résumé en cours..."):
                    summary = generate_summary(pdf_text, api_key, model)
                    
                    if summary:
                        st.session_state.summary = summary
                        st.success("✅ Résumé généré avec succès !")

# Affichage du résumé
if st.session_state.summary:
    st.markdown('<h2 class="sub-header">📊 Résumé Financier</h2>', unsafe_allow_html=True)
    
    # Métriques rapides
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Pages analysées", str(pdf_text.count("=== [PAGE")) if st.session_state.pdf_text else "0")
    with col2:
        st.metric("📊 Caractères", f"{len(st.session_state.pdf_text):,}" if st.session_state.pdf_text else "0")
    with col3:
        st.metric("🤖 Modèle utilisé", model)
    
    # Affichage du résumé
    st.markdown(st.session_state.summary)
    
    # Bouton de téléchargement
    st.download_button(
        label="💾 Télécharger le Résumé",
        data=st.session_state.summary,
        file_name="resume_financier.md",
        mime="text/markdown"
    )

# Section de questions interactives
if st.session_state.pdf_text:
    st.markdown('<h2 class="sub-header">❓ Questions Interactives</h2>', unsafe_allow_html=True)
    
    st.info("💡 Posez des questions spécifiques sur votre document financier")
    
    # Interface de chat
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input pour la question
    if prompt := st.chat_input("Posez votre question..."):
        # Ajouter la question à l'historique
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Afficher la question
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Générer la réponse
        with st.chat_message("assistant"):
            with st.spinner("🤔 Recherche de la réponse..."):
                response = answer_question(prompt, st.session_state.pdf_text, api_key, model)
                
                if response:
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                else:
                    st.error("❌ Impossible de générer une réponse")
    
    # Bouton pour effacer l'historique
    if st.session_state.chat_history:
        if st.button("🗑️ Effacer l'historique des questions", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🔒 Vos données restent confidentielles et ne sont pas stockées</p>
    <p>⚡ Propulsé par OpenRouter et Streamlit</p>
</div>
""", unsafe_allow_html=True)
