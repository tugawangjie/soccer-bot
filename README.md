# ⚽️ Soccer Bot

An LLM-powered soccer chatbot with lightweight RAG (retrieval-augmented generation) over a curated CSV of league data.  
Ask match or league questions in natural language and get concise answers grounded in the local dataset.

> Repo structure: `app.py`, `ragv2.py`, `prompts.py`, `combined_leagues.csv`, `requirements.txt`  
> UI: Streamlit app launched via `streamlit run app.py`.

---

## ✨ Features

- **Chat UI:** Streamlit interface for quick Q&A.  
- **RAG pipeline:** Looks up relevant rows from `combined_leagues.csv` before answering.  
- **Prompt presets:** Centralized prompt templates in `prompts.py` for easy tuning.  
- **Local & API-key friendly:** Runs locally; optional model/API config via environment variables.

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

1. **User question →** Streamlit UI (`app.py`) collects the input.  
2. **Retrieve rows →** `ragv2.py` filters or searches `combined_leagues.csv` for relevant rows (e.g., by team, league, or date).  
3. **Prompting →** `prompts.py` provides structured system and user prompts. Retrieved snippets are injected as context.  
4. **LLM answer →** The model generates a grounded response, displayed in the Streamlit interface.

---

## 🧪 Example Queries

- “Who won the last fixture between Team A and Team B?”  
- “Show me Team X’s recent results in League Y.”  
- “What’s the standing summary for League Z?”

> (Responses depend on the contents of `combined_leagues.csv`.)

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

**Empty or incorrect answers?**  
Verify that `combined_leagues.csv` exists, has the expected columns, and the retrieval logic matches the data format.

---

*Maintainers:* [@tugawangjie](https://github.com/tugawangjie) and contributors.
