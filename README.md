# ⚽️ Soccer Bot

An **LLM-powered soccer prediction and analysis app** with lightweight RAG (retrieval-augmented generation) over a curated CSV of league data.  
Instead of a chatbot, the Streamlit UI now provides **dropdown menus** for team selection and a **prediction button** that generates data-grounded match insights.

> Repo structure: `app.py`, `ragv2.py`, `prompts.py`, `combined_leagues.csv`, `requirements.txt`  
> UI: Streamlit app launched via `streamlit run app.py`.

---

## ✨ Features

- **Dropdown-based UI:** Select two teams from dropdowns and click **Predict** to generate match insights.  
- **RAG pipeline:** Retrieves relevant match data from `combined_leagues.csv` before prediction.  
- **LLM analysis:** The model uses contextual data to provide a clear, natural-language summary of likely outcomes.  
- **Prompt presets:** Centralized templates in `prompts.py` for tuning tone and logic.  
- **Local & API-key friendly:** Runs locally; optional model/API config via environment variables.  
- **Error handling:** If two teams haven’t played in over 3 years, the app displays a friendly message instead of failing.  

---

## 🚀 Quickstart

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/tugawangjie/soccer-bot.git
cd soccer-bot
```

### 2️⃣ Create & Activate a Virtual Environment

**macOS/Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Environment Variables (If Required)

If your app uses an LLM provider (e.g., OpenAI), add keys to a `.env` file in the repo root:

```
OPENAI_API_KEY=sk-xxxxxxxx
# Add other keys if used:
# TOGETHER_API_KEY=...
# GROQ_API_KEY=...
```

> If `app.py` reads from `os.getenv(...)`, a `.env` file will be automatically loaded when using `python-dotenv`.

### 5️⃣ Run the App

```bash
streamlit run app.py
```

Then open the local URL shown in your terminal (usually [http://localhost:8501](http://localhost:8501)).

---

## 🔎 How It Works

1. **User selection →** The Streamlit UI presents dropdown menus to choose a **Home Team** and **Away Team**.  
2. **Data retrieval →** `ragv2.py` filters or searches `combined_leagues.csv` for past results between the two teams.  
3. **Prompt construction →** `prompts.py` formats a structured prompt including recent match data.  
4. **Prediction →** The model generates a clear match analysis or prediction when the **“Predict”** button is clicked.  
5. **Error handling →** If the teams haven’t played in the last 3 years, a message notifies the user instead of producing an error.

---

## 🧪 Example Usage

- Select **Team A** and **Team B** from dropdowns.  
- Click **“Predict”** to generate insights.  
- Receive a grounded prediction like:  
  > “Based on recent form and head-to-head data, Team A is favored to win against Team B.”  

---

## 🧩 Improvements & Future Work

- **Prediction clarity:**  
  The app now generates analysis referring to **specific team names** (e.g., “Manchester City win”) rather than generic results like “Home win” or “Away win.” This helps reduce ambiguity and improve readability.  

- **Enhanced retrieval:**  
  Future updates may include form weighting, injury data, or additional league stats for more accurate predictions.

---

## 🛠️ Customization

- **Prompts:** Edit tone or logic in `prompts.py`.  
- **Retrieval:** Adjust similarity or keyword logic in `ragv2.py`.  
- **Data:** Replace or update `combined_leagues.csv` with your own schema and align retrieval code accordingly.  

---

## 📦 Requirements

Install via the included `requirements.txt`.  
If you add packages (e.g., `streamlit`, `pandas`, `python-dotenv`, LLM SDK), update the file:

```bash
pip freeze > requirements.txt
```

---

## 🤝 Contributing

1. Create a feature branch  
   ```bash
   git checkout -b feat/my-change
   ```
2. Commit your updates  
   ```bash
   git commit -m "feat: add X"
   ```
3. Push and open a pull request  
   ```bash
   git push origin feat/my-change
   ```

---

## 📄 License

Add a license of your choice (e.g., MIT, Apache 2.0) in a `LICENSE` file.

---

## 🙋 FAQ

**Streamlit not found?**  
Make sure your virtual environment is active and `streamlit` is installed:
```bash
pip install streamlit
```

**.env not loading?**  
Check that `python-dotenv` is installed and `load_dotenv()` is called in `app.py`.

**No prediction shown?**  
Ensure both teams are selected and that `combined_leagues.csv` contains recent match data for them.

---

*Maintainers:* [@tugawangjie](https://github.com/tugawangjie) and contributors.
