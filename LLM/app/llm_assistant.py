"""
Module pour l'assistant LLM avec OpenAI
"""

import os
from typing import List, Dict
import pandas as pd
from openai import OpenAI
import yaml
from pathlib import Path


class LLMAssistant:
    """Assistant LLM pour l'aide à la décision"""
    
    def __init__(self, config_path: str = "../config/llm_config.yaml"):
        """
        Initialise l'assistant LLM
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        # Charger la configuration (compatible Docker et local)
        if os.path.exists("/app/config/llm_config.yaml"):
            config_file = "/app/config/llm_config.yaml"
        else:
            config_file = Path(__file__).parent.parent / "config" / "llm_config.yaml"
        
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser le client OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY non trouvée dans les variables d'environnement")
        
        self.client = OpenAI(api_key=api_key)
        self.model = self.config['llm']['model']
        self.temperature = self.config['llm']['temperature']
        self.max_tokens = self.config['llm']['max_tokens']
        
        # Historique de conversation
        self.conversation_history = []
    
    def format_data_context(self, data: pd.DataFrame, query: str) -> str:
        """
        Formate les données en contexte pour le LLM
        
        Args:
            data: DataFrame avec les données pertinentes
            query: Question de l'utilisateur
            
        Returns:
            Contexte formaté
        """
        # Limiter le nombre de lignes pour ne pas dépasser les tokens
        max_rows = 50
        
        if len(data) > max_rows:
            # Prendre un échantillon représentatif
            data_sample = data.head(max_rows)
            context = f"Voici un échantillon des données ({max_rows} premières lignes sur {len(data)}) :\n\n"
        else:
            data_sample = data
            context = f"Voici les données complètes ({len(data)} lignes) :\n\n"
        
        # Convertir en format texte lisible
        context += data_sample.to_string(index=False)
        
        # Ajouter des statistiques résumées si beaucoup de données
        if len(data) > max_rows:
            context += f"\n\nStatistiques globales :\n"
            context += f"- Total de lignes : {len(data)}\n"
            
            if 'Predicted_Quantity' in data.columns:
                context += f"- Quantité totale : {data['Predicted_Quantity'].sum():,}\n"
                context += f"- Quantité moyenne : {data['Predicted_Quantity'].mean():.2f}\n"
                context += f"- Quantité min : {data['Predicted_Quantity'].min()}\n"
                context += f"- Quantité max : {data['Predicted_Quantity'].max()}\n"
            
            if 'City_State' in data.columns:
                context += f"- Nombre de villes : {data['City_State'].nunique()}\n"
            
            if 'Product' in data.columns:
                context += f"- Produits : {', '.join(data['Product'].unique())}\n"
        
        return context
    
    def ask(self, query: str, context_data: pd.DataFrame = None) -> str:
        """
        Pose une question à l'assistant
        
        Args:
            query: Question de l'utilisateur
            context_data: Données contextuelles (optionnel)
            
        Returns:
            Réponse de l'assistant
        """
        # Préparer les messages
        messages = [
            {"role": "system", "content": self.config['prompts']['system']}
        ]
        
        # Ajouter l'historique de conversation
        messages.extend(self.conversation_history)
        
        # Ajouter le contexte des données si fourni
        if context_data is not None and not context_data.empty:
            data_context = self.format_data_context(context_data, query)
            context_message = self.config['prompts']['context_template'].format(context=data_context)
            messages.append({"role": "system", "content": context_message})
        
        # Ajouter la question de l'utilisateur
        messages.append({"role": "user", "content": query})
        
        # Appeler l'API OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            # Mettre à jour l'historique
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            # Limiter l'historique à 10 messages (5 échanges)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return answer
            
        except Exception as e:
            return f"❌ Erreur lors de l'appel à l'API OpenAI : {str(e)}"
    
    def reset_conversation(self):
        """Réinitialise l'historique de conversation"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Récupère l'historique de conversation
        
        Returns:
            Liste des messages
        """
        return self.conversation_history
