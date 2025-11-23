"""
Module pour charger et préparer les données de prédiction
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Tuple


class DataLoader:
    """Charge et prépare les données de prédiction"""
    
    def __init__(self, monthly_path: str, daily_path: str):
        """
        Initialise le chargeur de données
        
        Args:
            monthly_path: Chemin vers le fichier CSV des prédictions mensuelles
            daily_path: Chemin vers le fichier CSV des prédictions journalières
        """
        self.monthly_path = Path(monthly_path)
        self.daily_path = Path(daily_path)
        self.monthly_df = None
        self.daily_df = None
    
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Charge les données depuis les fichiers CSV
        
        Returns:
            Tuple contenant (monthly_df, daily_df)
        """
        # Charger les données mensuelles
        self.monthly_df = pd.read_csv(self.monthly_path)
        
        # Charger les données journalières
        self.daily_df = pd.read_csv(self.daily_path)
        self.daily_df['Date'] = pd.to_datetime(self.daily_df['Date'])
        
        return self.monthly_df, self.daily_df
    
    def get_summary_stats(self) -> Dict:
        """
        Calcule des statistiques résumées sur les données
        
        Returns:
            Dictionnaire avec les statistiques
        """
        if self.monthly_df is None or self.daily_df is None:
            self.load_data()
        
        stats = {
            'total_predictions': len(self.daily_df),
            'products': self.monthly_df['Product'].unique().tolist(),
            'cities': self.monthly_df['City_State'].unique().tolist(),
            'months': sorted(self.monthly_df['Month'].unique().tolist()),
            'date_range': {
                'start': self.daily_df['Date'].min().strftime('%Y-%m-%d'),
                'end': self.daily_df['Date'].max().strftime('%Y-%m-%d')
            },
            'total_demand': {
                product: int(self.monthly_df[self.monthly_df['Product'] == product]['Predicted_Quantity'].sum())
                for product in self.monthly_df['Product'].unique()
            }
        }
        
        return stats
    
    def get_product_data(self, product: str) -> pd.DataFrame:
        """
        Récupère les données pour un produit spécifique
        
        Args:
            product: Nom du produit
            
        Returns:
            DataFrame filtré
        """
        if self.monthly_df is None:
            self.load_data()
        
        return self.monthly_df[self.monthly_df['Product'] == product].copy()
    
    def get_city_data(self, city_state: str) -> pd.DataFrame:
        """
        Récupère les données pour une ville spécifique
        
        Args:
            city_state: Nom de la ville (format: "City (State)")
            
        Returns:
            DataFrame filtré
        """
        if self.monthly_df is None:
            self.load_data()
        
        return self.monthly_df[self.monthly_df['City_State'] == city_state].copy()
    
    def compare_cities(self, city1: str, city2: str, product: str = None) -> pd.DataFrame:
        """
        Compare deux villes
        
        Args:
            city1: Première ville
            city2: Deuxième ville
            product: Produit à comparer (optionnel)
            
        Returns:
            DataFrame avec la comparaison
        """
        if self.monthly_df is None:
            self.load_data()
        
        df = self.monthly_df[self.monthly_df['City_State'].isin([city1, city2])].copy()
        
        if product:
            df = df[df['Product'] == product]
        
        return df
    
    def get_top_cities(self, product: str, n: int = 5) -> pd.DataFrame:
        """
        Récupère les top N villes par demande pour un produit
        
        Args:
            product: Nom du produit
            n: Nombre de villes à retourner
            
        Returns:
            DataFrame avec les top villes
        """
        if self.monthly_df is None:
            self.load_data()
        
        product_df = self.monthly_df[self.monthly_df['Product'] == product].copy()
        top_cities = (
            product_df
            .groupby('City_State')['Predicted_Quantity']
            .sum()
            .sort_values(ascending=False)
            .head(n)
            .reset_index()
        )
        
        return top_cities
    
    def calculate_growth(self, product: str = None) -> pd.DataFrame:
        """
        Calcule la croissance mensuelle par ville
        
        Args:
            product: Produit à analyser (optionnel)
            
        Returns:
            DataFrame avec les taux de croissance
        """
        if self.monthly_df is None:
            self.load_data()
        
        df = self.monthly_df.copy()
        if product:
            df = df[df['Product'] == product]
        
        # Pivoter pour avoir les mois en colonnes
        pivot = df.pivot_table(
            values='Predicted_Quantity',
            index=['Product', 'City_State'],
            columns='Month',
            aggfunc='sum'
        )
        
        # Calculer les croissances
        months = sorted(pivot.columns)
        if len(months) >= 2:
            # Croissance du premier au deuxième mois
            pivot['Growth_M1_M2'] = ((pivot[months[1]] - pivot[months[0]]) / pivot[months[0]] * 100).round(2)
            
            if len(months) >= 3:
                # Croissance du deuxième au troisième mois
                pivot['Growth_M2_M3'] = ((pivot[months[2]] - pivot[months[1]]) / pivot[months[1]] * 100).round(2)
                # Croissance totale
                pivot['Growth_Total'] = ((pivot[months[2]] - pivot[months[0]]) / pivot[months[0]] * 100).round(2)
        
        return pivot.reset_index()
