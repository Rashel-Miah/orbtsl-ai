# 🧠 Oracle Text-to-SQL Chatbot (LangChain + LangGraph + Streamlit)

This is a modular, production-grade chatbot that allows users to query an Oracle database using natural language via Streamlit. It uses LangChain, LangGraph, Ollama (Qwen2.5-coder), and FAISS for text-to-SQL generation with schema awareness and few-shot learning.

## 🧩 Project Structure

```
App/
├── .streamlit/
│   ├── config.toml               # Streamlit theme config
│   └── secrets.toml              # Database/API secrets
│
├── login.py                      # Streamlit login landing page
├── chatbot.py                    # Streamlit chatbot UI
│
├── chat/
│   └── (used internally by chatbot.py)
│
├── utils/
│   ├── examples.py               # Few-shot example loader
│   ├── oracle_connector.py       # Oracle DB connector with async pool
│   ├── prompt_utils.py           # Smart prompt builder from schema
│   ├── schema_store.py           # FAISS vector store for schema
│   ├── example_store.py          # FAISS vector store for examples
│   ├── langgraph_chain.py        # LangGraph-based SQL reasoning graph
│   ├── check_query_prompt.py     # Prompt for double-checking LLM-generated SQL
│
├── control/
│   ├── auth.py                   # User auth from Oracle + dynamic UI logic
│   ├── db.py                     # Raw Oracle connection helpers
│   └── rebuild_vector.py         # Vector index rebuild functions
│
├── data/
│   ├── examples.json             # Example question-query pairs
│   ├── schema_store.faiss        # FAISS vector index for schema
│   └── example_store.faiss       # FAISS vector index for few-shot examples
```

## 🚀 Features

- ✅ Natural Language → SQL translation using Ollama (`qwen2.5-coder`)
- ✅ Async Oracle DB querying with connection pool (`python-oracledb`)
- ✅ LangGraph-based execution flow (`Classify → Generate SQL → Run → Answer`)
- ✅ Dynamic prompt creation with relevant schema and examples
- ✅ FAISS-based vector search for few-shot selection and schema hints
- ✅ Auto rebuild schema/example vector store with cache clearing
- ✅ Multi-turn memory & conversational history
- ✅ Role-based login + menu using Oracle-backed users
- ✅ Streamlit UI with secure credentials and theme control

## 🛠 Setup Instructions

### 1. Clone the repo and enter the directory
```bash
git clone <your-repo>
cd App
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install and start Ollama
```bash
ollama pull qwen2.5-coder:7b
ollama run qwen2.5-coder:7b
```

### 4. Configure credentials
Edit `.streamlit/secrets.toml` to add your Oracle credentials:
```toml
DB_USER = "your_user"
DB_PASSWORD = "your_password"
DB_DSN = "localhost:1521/orcl"
```

### 5. Run the app
```bash
streamlit run login.py
```

## 🔁 Rebuilding Vector Stores (Optional)

To force rebuild schema or example vector store from source:

- Use buttons in the UI
- Or manually call:
```python
from schema_store import build_or_load_schema_store
from example_store import build_or_load_example_selector

build_or_load_schema_store.clear()
build_or_load_schema_store(force_rebuild=True)

build_or_load_example_selector.clear()
build_or_load_example_selector(force_rebuild=True)
```

## ✅ Security Notes

- Secrets like DB credentials should be stored in `secrets.toml`.
- All user logins are checked via Oracle DB from `control/auth.py`.

## 🤖 Model Info

This app uses:
- **LLM:** `qwen2.5-coder` via Ollama
- **Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`

## 📬 Feedback / Contributions

Built by [Rashel Sarker].  
Feel free to fork and customize. PRs welcome!