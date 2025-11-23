import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
from dotenv import load_dotenv

from data_loader import DataLoader
from llm_assistant import LLMAssistant
from query_analyzer import QueryAnalyzer

# Charger les variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Assistant d'Aide à la Décision",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        color: #000000 !important;
    }
    .user-message {
        background-color: #e3f2fd;
        color: #000000 !important;
    }
    .assistant-message {
        background-color: #f5f5f5;
        color: #000000 !important;
    }
    /* Forcer le texte noir dans tous les éléments */
    .stChatMessage {
        color: #000000 !important;
    }
    .stChatMessage p {
        color: #000000 !important;
    }
    .stChatMessage div {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_components():
    """Initialise les composants de l'application"""
    # Chemins vers les données (compatible Docker et local)
    if os.path.exists("/app/prediction"):
        # Environnement Docker
        monthly_path = "/app/prediction/predictions_3_mois.csv"
        daily_path = "/app/prediction/predictions_60_jours.csv"
    else:
        # Environnement local
        base_path = Path(__file__).parent.parent.parent
        monthly_path = base_path / "prediction" / "predictions_3_mois.csv"
        daily_path = base_path / "prediction" / "predictions_60_jours.csv"
    
    # Initialiser les composants
    data_loader = DataLoader(str(monthly_path), str(daily_path))
    data_loader.load_data()
    
    llm_assistant = LLMAssistant()
    query_analyzer = QueryAnalyzer(data_loader)
    
    return data_loader, llm_assistant, query_analyzer


def display_sidebar(data_loader):
    """Affiche la barre latérale avec les statistiques"""
    st.sidebar.title("📊 Vue d'ensemble")
    
    stats = data_loader.get_summary_stats()
    
    st.sidebar.metric("Total de prédictions", f"{stats['total_predictions']:,}")
    
    st.sidebar.markdown("### Produits")
    for product in stats['products']:
        demand = stats['total_demand'][product]
        st.sidebar.metric(product, f"{demand:,} unités")
    
    st.sidebar.markdown("### Période")
    st.sidebar.info(f"📅 {stats['date_range']['start']} → {stats['date_range']['end']}")
    
    st.sidebar.markdown("### Villes couvertes")
    st.sidebar.write(f"{len(stats['cities'])} villes")
    with st.sidebar.expander("Voir la liste"):
        for city in sorted(stats['cities']):
            st.write(f"• {city}")
    
    # Questions suggérées
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Questions suggérées")
    
    suggested_questions = [
        "Où devrais-je augmenter les stocks de ThinkPad Laptop ?",
        "Quelle ville montre la plus forte progression de la demande ?",
        "Compare la demande entre Dallas (TX) et Austin (TX)",
        "Quelles sont les 5 villes avec la plus forte demande de batteries ?",
        "Quelle est la tendance de la demande pour mars à mai ?",
    ]
    
    for i, question in enumerate(suggested_questions):
        if st.sidebar.button(question, key=f"suggest_{i}"):
            st.session_state.suggested_question = question


def display_visualizations(data_loader):
    """Affiche les visualisations des données"""
    st.markdown("## 📈 Visualisations")
    
    monthly_df = data_loader.monthly_df
    
    # Sélection du produit
    col1, col2 = st.columns(2)
    with col1:
        selected_product = st.selectbox(
            "Sélectionner un produit",
            options=monthly_df['Product'].unique()
        )
    
    # Filtrer les données
    product_df = monthly_df[monthly_df['Product'] == selected_product]
    
    # Graphique 1: Demande par ville et mois
    fig1 = px.bar(
        product_df,
        x='City_State',
        y='Predicted_Quantity',
        color='Month',
        title=f"Demande de {selected_product} par ville et mois",
        labels={'Predicted_Quantity': 'Quantité prédite', 'City_State': 'Ville'},
        barmode='group'
    )
    fig1.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Graphique 2: Évolution temporelle
    monthly_total = product_df.groupby('Month')['Predicted_Quantity'].sum().reset_index()
    fig2 = px.line(
        monthly_total,
        x='Month',
        y='Predicted_Quantity',
        title=f"Évolution de la demande totale - {selected_product}",
        labels={'Predicted_Quantity': 'Quantité totale', 'Month': 'Mois'},
        markers=True
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Graphique 3: Top 10 villes
    top_cities = product_df.groupby('City_State')['Predicted_Quantity'].sum().sort_values(ascending=False).head(10)
    fig3 = px.bar(
        x=top_cities.values,
        y=top_cities.index,
        orientation='h',
        title=f"Top 10 villes - {selected_product}",
        labels={'x': 'Quantité totale', 'y': 'Ville'}
    )
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, use_container_width=True)


def display_chat_interface(llm_assistant, query_analyzer):
    """Affiche l'interface de chat"""
    st.markdown("## 💬 Assistant d'Aide à la Décision")
    
    # Initialiser l'historique de chat dans session_state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Afficher l'historique de chat
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f'<div class="chat-message user-message" style="color: #000000;"><strong>👤 Vous:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message" style="color: #000000;"><strong>🤖 Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Zone de saisie
    user_query = st.text_input(
        "Posez votre question :",
        key="user_input",
        placeholder="Ex: Où devrais-je augmenter les stocks de ThinkPad Laptop ?"
    )
    
    # Gérer les questions suggérées
    if 'suggested_question' in st.session_state:
        user_query = st.session_state.suggested_question
        del st.session_state.suggested_question
    
    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("📤 Envoyer", type="primary")
    with col2:
        if st.button("🔄 Nouvelle conversation"):
            st.session_state.chat_history = []
            llm_assistant.reset_conversation()
            st.rerun()
    
    if send_button and user_query:
        # Ajouter la question à l'historique
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })
        
        # Analyser la requête et obtenir les données pertinentes
        with st.spinner("🔍 Analyse de votre question..."):
            query_summary = query_analyzer.get_query_summary(user_query)
            relevant_data = query_analyzer.get_relevant_data(user_query)
            
            # Afficher les informations extraites (debug)
            with st.expander("ℹ️ Informations détectées"):
                st.write(f"**Intention:** {query_summary['intent']}")
                if query_summary['product']:
                    st.write(f"**Produit:** {query_summary['product']}")
                if query_summary['cities']:
                    st.write(f"**Villes:** {', '.join(query_summary['cities'])}")
                st.write(f"**Données pertinentes:** {len(relevant_data)} lignes")
        
        # Obtenir la réponse de l'assistant
        with st.spinner("🤖 Génération de la réponse..."):
            response = llm_assistant.ask(user_query, relevant_data)
        
        # Ajouter la réponse à l'historique
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # Recharger la page pour afficher la nouvelle conversation
        st.rerun()


def main():
    """Fonction principale de l'application"""
    # En-tête
    st.markdown('<h1 class="main-header">📊 Assistant d\'Aide à la Décision</h1>', unsafe_allow_html=True)
    st.markdown("### Analyse intelligente des prédictions de demande")
    
    # Vérifier la clé API
    if not os.getenv('OPENAI_API_KEY'):
        st.error("❌ OPENAI_API_KEY non trouvée. Veuillez créer un fichier .env avec votre clé API.")
        st.info("💡 Copiez .env.example vers .env et ajoutez votre clé API OpenAI")
        st.stop()
    
    # Initialiser les composants
    try:
        data_loader, llm_assistant, query_analyzer = initialize_components()
    except Exception as e:
        st.error(f"❌ Erreur lors de l'initialisation : {str(e)}")
        st.stop()
    
    # Afficher la barre latérale
    display_sidebar(data_loader)
    
    # Onglets principaux
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📈 Visualisations", "📊 Données"])
    
    with tab1:
        display_chat_interface(llm_assistant, query_analyzer)
    
    with tab2:
        display_visualizations(data_loader)
    
    with tab3:
        st.markdown("## 📊 Données de Prédiction")
        
        # Sélection du type de données
        data_type = st.radio(
            "Type de données",
            options=["Mensuelles", "Journalières"],
            horizontal=True
        )
        
        if data_type == "Mensuelles":
            st.dataframe(data_loader.monthly_df, use_container_width=True)
            st.download_button(
                "📥 Télécharger (CSV)",
                data_loader.monthly_df.to_csv(index=False).encode('utf-8'),
                "predictions_mensuelles.csv",
                "text/csv"
            )
        else:
            st.dataframe(data_loader.daily_df, use_container_width=True)
            st.download_button(
                "📥 Télécharger (CSV)",
                data_loader.daily_df.to_csv(index=False).encode('utf-8'),
                "predictions_journalieres.csv",
                "text/csv"
            )


if __name__ == "__main__":
    main()
