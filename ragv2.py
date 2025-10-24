
from typing import Optional
from prompts import genAI_soccer_prompt_zeroshot
import faiss
import os
import pandas as pd
from tqdm import tqdm
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore


# Setup environment variables
os.environ['OPENAI_API_KEY'] = 'lm-studio'
os.environ['OPENAI_API_BASE'] = 'http://localhost:1234/v1'

# Vector dimension (adjust based on your embedding model)
d = 768

class SoccerMatchPredictor:
    def __init__(self, historical_data_path: Optional[str] = None):
        self.index = None
        self.historical_data_df = None
        
        if historical_data_path:
            self.build_knowledge_base(historical_data_path)
    
    def build_knowledge_base(self, historical_data_path: str):
        """Build the soccer RAG knowledge base from historical match data."""
        print("Building soccer matches knowledge base...")
        
        # Load historical match data
        self.historical_data_df = pd.read_csv(historical_data_path)
        
        # Create documents with match data
        documents = []
        for _, row in self.historical_data_df.iterrows():
            # Format the match information in a structured way
            try:
                home_score = 0 if pd.isna(row['home_score']) else int(float(row['home_score']))
                away_score = 0 if pd.isna(row['away_score']) else int(float(row['away_score']))
                matchday = 0 if pd.isna(row['matchday']) else int(float(row['matchday']))
                
                match_info = {
                    'home_team': row['home_team'],
                    'away_team': row['away_team'],
                    'home_score': home_score,
                    'away_score': away_score,
                    'date': row['utcDate'],
                    'competition': row['source_file'].replace('_2023_2025.csv', '').replace('_', ' '),
                    'stage': row['stage'].replace('_', ' ').title() if not pd.isna(row['stage']) else 'Regular Season',
                    'season': str(row['season']),
                    'matchday': f"Matchday {matchday}",
                    'winner': row['winner'] if not pd.isna(row['winner']) else 'Not Played'
                }
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
            
            # Create a document with match details and outcome
            try:
                doc_text = (
                    f"Match: {match_info['home_team']} vs {match_info['away_team']}\n"
                    f"Competition: {match_info['competition']}\n"
                    f"Stage: {match_info['stage']}\n"
                    f"Season: {match_info['season']}\n"
                    f"Date: {match_info['date']}\n"
                    f"{match_info['matchday']}\n"
                    f"Score: {match_info['home_team']} {match_info['home_score']} - {match_info['away_score']} {match_info['away_team']}\n"
                    f"Result: {match_info['winner'].replace('_', ' ').title() if '_' in match_info['winner'] else match_info['winner']}"
                )
                documents.append(Document(text=doc_text))
            except Exception as e:
                print(f"Error creating document: {e}")
                continue
        
        # Build FAISS index
        faiss_index = faiss.IndexFlatL2(d)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        print(f"Indexing {len(documents)} historical matches...")
        self.index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context,
            show_progress=True
        )
        print("Knowledge base built successfully!")
    
    def predict_match(self, home_team: str, away_team: str, competition: str = None) -> str:
        """Generate a prediction for a match between two teams using RAG."""
        if self.index is None:
            return "ERROR: Knowledge base not built"
        
        try:
            # Create query about the match, including competition if provided
            match_query = f"{home_team} vs {away_team}"
            if competition:
                match_query += f" in {competition}"
            
            # Get retriever results with different strategies
            retriever = self.index.as_retriever(similarity_top_k=10)  # Get more matches initially
            retrieved_nodes = retriever.retrieve(match_query)
            
            # Filter and sort retrieved matches
            relevant_matches = []
            h2h_matches = []
            recent_home_matches = []
            recent_away_matches = []
            
            for node in retrieved_nodes:
                match_text = node.text
                
                # Check if it's a head-to-head match
                if (home_team in match_text and away_team in match_text):
                    h2h_matches.append(node)
                # Check recent matches of home team
                elif home_team in match_text:
                    recent_home_matches.append(node)
                # Check recent matches of away team
                elif away_team in match_text:
                    recent_away_matches.append(node)
            
            # Format retrieved examples with categorization
            historical_matches = ""
            
            # Add head-to-head matches first
            if h2h_matches:
                historical_matches += "Head-to-Head Matches:\n"
                for i, node in enumerate(h2h_matches[:3], 1):
                    historical_matches += f"{node.text}\n\n"
            
            # Add recent home team matches
            if recent_home_matches:
                historical_matches += f"\nRecent {home_team} Matches:\n"
                for i, node in enumerate(recent_home_matches[:3], 1):
                    historical_matches += f"{node.text}\n\n"
            
            # Add recent away team matches
            if recent_away_matches:
                historical_matches += f"\nRecent {away_team} Matches:\n"
                for i, node in enumerate(recent_away_matches[:3], 1):
                    historical_matches += f"{node.text}\n\n"
            
            # Construct the RAG query
            rag_query = f"""
            {genAI_soccer_prompt_zeroshot}
            
            Here are some relevant historical matches:
            
            {historical_matches}
            
            Based on these historical matches, provide a prediction for:
            {home_team} vs {away_team}
            """
            
            # Use query engine to get response
            response = self.index.as_query_engine().query(rag_query)
            
            return response.response.strip()
            
        except Exception as e:
            print(f"Prediction Error: {e}")
            return "ERROR: Match prediction failed"

def interactive_predictions():
    """Interactive command-line interface for match predictions."""
    historical_data_file = 'soccer_matches_history.csv'
    
    try:
        # Initialize the predictor
        predictor = SoccerMatchPredictor(historical_data_file)
        
        while True:
            print("\n=== Soccer Match Predictor ===")
            print("Enter team names as they appear in the official data")
            print("For example: 'Arsenal FC' instead of 'Arsenal'")
            
            home_team = input("Enter home team (or 'quit' to exit): ").strip()
            if home_team.lower() == 'quit':
                break
                
            away_team = input("Enter away team: ").strip()
            
            competitions = ['UEFA Champions League', 'Premier League', 'La Liga', 
                          'Bundesliga', 'Serie A', 'Ligue 1']
            print("\nCompetitions:")
            for i, comp in enumerate(competitions, 1):
                print(f"{i}. {comp}")
            
            comp_choice = input("\nEnter competition number (or press Enter to skip): ").strip()
            competition = None
            if comp_choice.isdigit() and 1 <= int(comp_choice) <= len(competitions):
                competition = competitions[int(comp_choice) - 1]
            
            print("\nGenerating prediction...")
            prediction = predictor.predict_match(home_team, away_team, competition)
            
            print("\nPrediction:")
            print("-" * 50)
            print(prediction)
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    # Test the predictor
    predictor = SoccerMatchPredictor()
    predictor.build_knowledge_base('combined_leagues.csv')
    
    # Example prediction
    print(predictor.predict_match("Manchester City FC", "Arsenal FC"))