"""
Module pour analyser les questions et extraire les données pertinentes
"""

import re
from typing import Dict, Optional, List
import pandas as pd
from data_loader import DataLoader


class QueryAnalyzer:
    """Analyse les questions utilisateur et extrait les données pertinentes"""
    
    def __init__(self, data_loader: DataLoader):
        """
        Initialise l'analyseur de requêtes
        
        Args:
            data_loader: Instance de DataLoader
        """
        self.data_loader = data_loader
        
        # Patterns pour détecter les intentions
        self.patterns = {
            'stock_increase': r'(augment|stock|approvision|commander|livr)',
            'comparison': r'(compar|versus|vs|différence|entre)',
            'growth': r'(progress|croissance|évolu|augment|tendance)',
            'top_cities': r'(top|meilleur|plus fort|classement)',
            'specific_city': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([A-Z]{2})\)',
            'product_thinkpad': r'(thinkpad|laptop|ordinateur)',
            'product_batteries': r'(batter|pile|aaa)',
            'month': r'(mars|avril|mai|march|april|may|2020-0[3-5])',
        }
        
        # Mapping des villes (pour gérer les variations)
        self.city_mapping = {
            'dallas': 'Dallas (TX)',
            'houston': 'Houston (TX)',
            'austin': 'Austin (TX)',
            'san francisco': 'San Francisco (CA)',
            'los angeles': 'Los Angeles (CA)',
            'new york': 'New York City (NY)',
            'boston': 'Boston (MA)',
            'seattle': 'Seattle (WA)',
            'atlanta': 'Atlanta (GA)',
            'portland': 'Portland (ME)',
            'washington': 'Washington DC',
        }
    
    def extract_cities(self, query: str) -> List[str]:
        """
        Extrait les noms de villes de la requête
        
        Args:
            query: Question de l'utilisateur
            
        Returns:
            Liste des villes trouvées
        """
        cities = []
        query_lower = query.lower()
        
        # Chercher les villes dans le mapping
        for city_key, city_full in self.city_mapping.items():
            if city_key in query_lower:
                cities.append(city_full)
        
        # Chercher les patterns "City (ST)"
        matches = re.findall(self.patterns['specific_city'], query)
        for match in matches:
            city_name, state = match
            city_full = f"{city_name} ({state})"
            if city_full not in cities:
                cities.append(city_full)
        
        return cities
    
    def extract_product(self, query: str) -> Optional[str]:
        """
        Extrait le produit de la requête
        
        Args:
            query: Question de l'utilisateur
            
        Returns:
            Nom du produit ou None
        """
        query_lower = query.lower()
        
        if re.search(self.patterns['product_thinkpad'], query_lower):
            return 'ThinkPad Laptop'
        elif re.search(self.patterns['product_batteries'], query_lower):
            return 'AAA Batteries (4-pack)'
        
        return None
    
    def detect_intent(self, query: str) -> str:
        """
        Détecte l'intention de la requête
        
        Args:
            query: Question de l'utilisateur
            
        Returns:
            Type d'intention détecté
        """
        query_lower = query.lower()
        
        if re.search(self.patterns['comparison'], query_lower):
            return 'comparison'
        elif re.search(self.patterns['growth'], query_lower):
            return 'growth'
        elif re.search(self.patterns['top_cities'], query_lower):
            return 'top_cities'
        elif re.search(self.patterns['stock_increase'], query_lower):
            return 'stock_increase'
        else:
            return 'general'
    
    def get_relevant_data(self, query: str) -> pd.DataFrame:
        """
        Récupère les données pertinentes pour la requête
        
        Args:
            query: Question de l'utilisateur
            
        Returns:
            DataFrame avec les données pertinentes
        """
        # Détecter l'intention
        intent = self.detect_intent(query)
        
        # Extraire les entités
        cities = self.extract_cities(query)
        product = self.extract_product(query)
        
        # Charger les données si nécessaire
        if self.data_loader.monthly_df is None:
            self.data_loader.load_data()
        
        # Filtrer les données selon l'intention
        if intent == 'comparison' and len(cities) >= 2:
            # Comparaison entre villes
            data = self.data_loader.compare_cities(cities[0], cities[1], product)
        
        elif intent == 'growth':
            # Analyse de croissance
            data = self.data_loader.calculate_growth(product)
            if cities:
                # Filtrer par villes si spécifiées
                data = data[data['City_State'].isin(cities)]
        
        elif intent == 'top_cities':
            # Top villes
            if product:
                top_cities = self.data_loader.get_top_cities(product, n=10)
                # Joindre avec les données mensuelles pour plus de détails
                data = self.data_loader.monthly_df[
                    (self.data_loader.monthly_df['Product'] == product) &
                    (self.data_loader.monthly_df['City_State'].isin(top_cities['City_State']))
                ]
            else:
                data = self.data_loader.monthly_df.copy()
        
        elif intent == 'stock_increase':
            # Recommandations de stock
            if product:
                data = self.data_loader.get_product_data(product)
            else:
                data = self.data_loader.monthly_df.copy()
            
            if cities:
                data = data[data['City_State'].isin(cities)]
        
        else:
            # Requête générale
            data = self.data_loader.monthly_df.copy()
            
            # Filtrer par produit si spécifié
            if product:
                data = data[data['Product'] == product]
            
            # Filtrer par villes si spécifiées
            if cities:
                data = data[data['City_State'].isin(cities)]
        
        return data
    
    def get_query_summary(self, query: str) -> Dict:
        """
        Résume les informations extraites de la requête
        
        Args:
            query: Question de l'utilisateur
            
        Returns:
            Dictionnaire avec les informations extraites
        """
        return {
            'intent': self.detect_intent(query),
            'cities': self.extract_cities(query),
            'product': self.extract_product(query),
            'query': query
        }
