import streamlit as st
import pandas as pd
from ragv2 import SoccerMatchPredictor
import os
import time

# Set page config
st.set_page_config(
    page_title="Soccer Match Predictor",
    page_icon="⚽",
    layout="wide"
)

# Initialize session states
if 'predictor' not in st.session_state:
    st.session_state.predictor = None
if 'is_initialized' not in st.session_state:
    st.session_state.is_initialized = False
if 'data_file' not in st.session_state:
    st.session_state.data_file = None

def initialize_knowledge_base():
    """Initialize the FAISS index and load the knowledge base"""
    try:
        with st.spinner("🔄 Loading match data..."):
            if not os.path.exists(st.session_state.data_file):
                st.error(f"File not found: {st.session_state.data_file}")
                return False
            
            # Create progress container
            progress_container = st.empty()
            progress_bar = st.progress(0)
            
            # Initialize predictor
            predictor = SoccerMatchPredictor()
            
            # Show DataFrame preview
            df = pd.read_csv(st.session_state.data_file)
            st.write("Preview of the match data:")
            st.dataframe(df.head(), hide_index=True)
            
            # Update progress
            progress_container.text("⚙️ Creating FAISS index...")
            progress_bar.progress(25)
            
            # Build knowledge base
            predictor.build_knowledge_base(st.session_state.data_file)
            progress_bar.progress(75)
            
            # Store in session state
            st.session_state.predictor = predictor
            st.session_state.is_initialized = True
            
            # Final update
            progress_container.text("✅ Knowledge base initialized successfully!")
            progress_bar.progress(100)
            
            # Clear progress indicators after a short delay
            time.sleep(1)
            progress_container.empty()
            progress_bar.empty()
            
            return True
            
    except Exception as e:
        st.error(f"Error initializing knowledge base: {str(e)}")
        return False

# Main app layout
st.title("⚽ Soccer Match Predictor")
st.write("Get AI-powered predictions for soccer matches based on historical data!")

# Sidebar for statistics and info
with st.sidebar:
    st.header("About")
    st.write("""
    This app uses RAG (Retrieval Augmented Generation) technology to analyze historical match data 
    and generate predictions for soccer matches. The predictions are based on:
    - Historical match results
    - Head-to-head records
    - Home/Away performance
    - Recent form
    """)
    
    if st.session_state.predictor is not None and st.session_state.predictor.historical_data_df is not None:
        st.header("Dataset Statistics")
        df = st.session_state.predictor.historical_data_df
        st.write(f"Total matches: {len(df)}")
        if 'utcDate' in df.columns:
            st.write(f"Date range: {df['utcDate'].min()} to {df['utcDate'].max()}")
        if 'source_file' in df.columns:
            leagues = df['source_file'].str.replace('_2023_2025.csv', '').str.replace('_', ' ').unique()
            st.write(f"Leagues: {', '.join(sorted(leagues))}")
        if 'season' in df.columns:
            st.write(f"Seasons: {', '.join(map(str, sorted(df['season'].unique())))}")
        st.write(f"Teams: {len(set(df['home_team'].unique()) | set(df['away_team'].unique()))}")# Initialize section
if not st.session_state.is_initialized:
    st.markdown("### 📚 Initialize Knowledge Base")
    st.write("Using the combined leagues dataset for predictions.")
    st.session_state.data_file = 'combined_leagues.csv'
    
    if st.session_state.data_file:
        if st.button("🚀 Initialize Knowledge Base"):
            if initialize_knowledge_base():
                st.success("✅ Knowledge base is ready! You can now make predictions.")
            
else:
    # Main prediction interface
    st.markdown("### ⚽ Make Predictions")
    
    # Get all available teams
    if st.session_state.predictor and st.session_state.predictor.historical_data_df is not None:
        all_teams = sorted(list(set(
            list(st.session_state.predictor.historical_data_df['home_team'].unique()) + 
            list(st.session_state.predictor.historical_data_df['away_team'].unique())
        )))
        
        col1, col2 = st.columns(2)
        
        with col1:
            home_team = st.selectbox("Home Team", all_teams, index=None)
            
        with col2:
            # Filter out the selected home team from away team options
            away_teams = [team for team in all_teams if team != home_team] if home_team else all_teams
            away_team = st.selectbox("Away Team", away_teams, index=None)

    # Prediction button
    if st.button("Get Prediction", disabled=not (home_team and away_team)):
        try:
            if st.session_state.predictor is not None:
                with st.spinner("Analyzing match data..."):
                    prediction = st.session_state.predictor.predict_match(home_team, away_team)
                    
                    # Display prediction in a nice format
                    st.markdown("### 🎯 Match Prediction")
                    st.markdown("---")
                    
                    # Parse prediction components
                    prediction_lines = prediction.split('\n')
                    
                    for line in prediction_lines:
                        if line.startswith("Prediction:"):
                            result = line.split(":")[1].strip()
                            if "Home Win" in result:
                                st.markdown(f"### 🏠 {line}")
                            elif "Away Win" in result:
                                st.markdown(f"### ✈️ {line}")
                            else:
                                st.markdown(f"### 🤝 {line}")
                        elif line.startswith("Reasoning:"):
                            st.markdown("#### 📝 Analysis")
                            st.write(line.split(":")[1].strip())
                        elif line.startswith("Confidence:"):
                            st.markdown("#### 📊 Confidence Level")
                            try:
                                confidence = line.split(":")[1].strip().rstrip('%')
                                confidence_value = float(confidence) / 100
                                st.progress(confidence_value)
                                st.write(f"{confidence}%")
                            except ValueError:
                                st.write(confidence)
                    
                    # Show relevant historical matches
                    st.markdown("### 📊 Recent Head-to-Head Matches")
                    if hasattr(st.session_state.predictor, 'historical_data_df'):
                        df = st.session_state.predictor.historical_data_df
                        h2h_matches = df[
                            ((df['home_team'] == home_team) & (df['away_team'] == away_team)) |
                            ((df['home_team'] == away_team) & (df['away_team'] == home_team))
                        ].sort_values('date', ascending=False).head(5)
                        
                        if not h2h_matches.empty:
                            st.dataframe(
                                h2h_matches[['date', 'home_team', 'home_score', 'away_score', 'away_team']],
                                hide_index=True
                            )
                        else:
                            st.info("No direct head-to-head matches found in the database.")
            else:
                st.error("Prediction system not initialized. Please initialize the knowledge base first.")
        except Exception as e:
            st.error(f"Error generating prediction: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Your Team")