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
# new flag to start initialization from button click
if 'start_init' not in st.session_state:
    st.session_state.start_init = False

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

    # Button sets a flag; actual long init happens below so Streamlit reruns cleanly
    if st.button("🚀 Initialize Knowledge Base", key="init_button"):
        st.session_state.start_init = True

    # When flag is set, perform the initialization once
    if st.session_state.start_init:
        succeeded = initialize_knowledge_base()
        st.session_state.start_init = False
        if succeeded:
            st.success("✅ Knowledge base is ready! You can now make predictions.")
else:
    # Main prediction interface
    st.markdown("### ⚽ Make Predictions")

    # Initialize selection variables
    home_team = None
    away_team = None

    # Show dropdowns only after the knowledge base is initialized
    if st.session_state.is_initialized and st.session_state.predictor and getattr(st.session_state.predictor, 'historical_data_df', None) is not None:
        df = st.session_state.predictor.historical_data_df

        # Build team list safely (drop NaNs, cast to str, dedupe, sort)
        teams_series = pd.concat([
            df.get('home_team', pd.Series([], dtype=object)),
            df.get('away_team', pd.Series([], dtype=object))
        ]).dropna().astype(str)
        all_teams = sorted(list(pd.unique(teams_series)), key=lambda s: s.lower())

        if not all_teams:
            st.warning("No teams found in the dataset.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                home_team = st.selectbox("Home Team", all_teams, key="home_team_select")
            with col2:
                away_options = [t for t in all_teams if t != home_team] if home_team else all_teams
                away_team = st.selectbox("Away Team", away_options, key="away_team_select")
    else:
        st.info("Initialize the knowledge base to enable team selection and predictions.")

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

                        # Find matches between the two teams
                        matches_df = df[
                            ((df['home_team'] == home_team) & (df['away_team'] == away_team)) |
                            ((df['home_team'] == away_team) & (df['away_team'] == home_team))
                        ].copy()

                        # If no matches at all in DB, treat as "no matches in past 3 years"
                        if matches_df.empty:
                            st.info(f"No matches between **{home_team}** and **{away_team}** were found in the database. Treating this as no matches in the past 3 years.")
                        else:
                            # Detect a date-like column
                            date_col = next((c for c in ['date', 'utcDate', 'utc_date', 'match_date'] if c in matches_df.columns), None)
                            if date_col:
                                # parse dates safely and normalize to UTC so comparisons are consistent
                                matches_df[date_col] = pd.to_datetime(matches_df[date_col], errors='coerce', utc=True)
                                matches_df = matches_df.sort_values(date_col, ascending=False)

                                # use a UTC-aware cutoff timestamp
                                three_years_ago = pd.Timestamp.now(tz='UTC') - pd.DateOffset(years=3)

                                recent = matches_df[matches_df[date_col] >= three_years_ago]
                                if recent.empty:
                                    st.info(f"No matches between **{home_team}** and **{away_team}** in the past 3 years.")
                                else:
                                    st.dataframe(
                                        recent[[date_col, 'home_team', 'home_score', 'away_score', 'away_team']].head(5),
                                        hide_index=True
                                    )
                            else:
                                # No date column available — cannot compute recency.
                                st.info(f"No date information available for historical matches. Treating this as no matches in the past 3 years between **{home_team}** and **{away_team}**.")
            else:
                st.error("Prediction system not initialized. Please initialize the knowledge base first.")
        except Exception as e:
            st.error(f"Error generating prediction: {str(e)}")

# Footer chatbox - place above footer
# Initialize chat history state (only once)
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # list of dicts: {"role": "user"/"assistant", "text": "..."}

if 'chat_input' not in st.session_state:
    st.session_state.chat_input = ""

# Callback for sending chat (runs before widget rendering completes)
def _send_chat_callback():
    query = st.session_state.get("chat_input", "").strip()
    if not query:
        # store a small flag to show an info message after widgets render
        st.session_state['_chat_info'] = "Please enter a question before sending."
        return

    # append user message
    st.session_state.chat_history.append({"role": "user", "text": query})

    # generate assistant reply
    if st.session_state.get("predictor") is not None and hasattr(st.session_state.predictor, "answer_query"):
        try:
            # call predictor (may block; consider running asynchronously if needed)
            reply = st.session_state.predictor.answer_query(query)
        except Exception as e:
            reply = f"Error generating reply: {e}"
    else:
        reply = ("Knowledge base not initialized. Please initialize it to enable chat."
                 if st.session_state.get("predictor") is None
                 else "Predictor does not implement answer_query(question: str) -> str.")

    st.session_state.chat_history.append({"role": "assistant", "text": reply})

    # clear input (allowed inside callback)
    st.session_state.chat_input = ""
    # clear any leftover info flag
    st.session_state.pop('_chat_info', None)

def _clear_chat_callback():
    st.session_state.chat_history = []
    st.session_state.chat_input = ""
    st.session_state['_chat_cleared'] = True

st.markdown("### 💬 Chat with the Knowledge Base")
st.write("Ask questions about the dataset, teams, or matches. The chat uses the initialized knowledge base for answers.")

# Single chat input area (unique key 'chat_input')
st.text_area("Your question", value=st.session_state.chat_input, key="chat_input", height=100, placeholder="Type a question and press Send...")

col1, col2 = st.columns([1, 1])
with col1:
    # Use callbacks so session_state changes happen in callbacks (avoids StreamlitDuplicate/modify errors)
    st.button("Send", key="send_chat", on_click=_send_chat_callback)

with col2:
    st.button("Clear Chat", key="clear_chat", on_click=_clear_chat_callback)

# Info messages set inside callbacks
if st.session_state.pop('_chat_info', None):
    st.info("Please enter a question before sending.")
if st.session_state.pop('_chat_cleared', None):
    st.success("Chat cleared.")

# Display chat history
if st.session_state.chat_history:
    st.markdown("----")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['text']}")
        else:
            st.markdown(f"**Assistant:** {msg['text']}")

# Footer (chat feature removed)
st.markdown("---")
st.markdown("Made with ❤️ by Your Team")
