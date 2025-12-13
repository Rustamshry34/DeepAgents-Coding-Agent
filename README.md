# 🧠 DeepAgents Coding Assistant

An autonomous coding agent powered by LangChain DeepAgents, local LLM (Ollama), Tavily search, and sandboxed Docker execution—packed in a gorgeous Streamlit chat UI.


| Feature    | How it helps                                              |
| ---------- | --------------------------------------------------------- |
| **Plan**   | Breaks big tasks into ordered TODOs via planner sub-agent |
| **Code**   | Generates type-hinted, PEP-8 compliant Python             |
| **Review** | Self-critiques for bugs, style, performance               |
| **Search** | Real-time web lookup for docs, examples, issues           |
| **Run**    | Executes code in an isolated Docker container             |
| **Ship**   | Packages the workspace into a downloadable ZIP            |


## ⚙️ 30-second setup

Clone & enter

```bash
git clone https://github.com/your-org/deepagents-coding.git
cd deepagents-coding
```


Install

```bash
python -m venv .venv && source .venv/bin/activate  # Win: .venv\Scripts\activate
pip install -r requirements.txt
```


## Setup Requirements

1. Make sure you have Ollama running with a model (e.g., qwen3:0.6b) available
2. Install requirements: `pip install -r requirements.txt`
3. Install langchain_ollama: `pip install langchain_ollama`
4. Set up your Tavily API key as an environment variable: `TAVILY_API_KEY=your_key_here`

## Run Ollama (local LLM)

```bash
ollama pull qwen3-coder:30b
ollama serve
```

## Running the Application

```bash
streamlit run app.py
```

## 🧪 Example prompts

| Prompt                                                               | What happens                     |
| -------------------------------------------------------------------- | -------------------------------- |
| `Build a FastAPI micro-service with JWT auth and a /search endpoint` | Planner → Coder → Reviewer → ZIP |
| `Scrape the top 10 Hacker News stories and save to CSV`              | Search → Code → Run → Download   |
| `Refactor this repo to use SQLModel instead of raw SQL`              | Upload → Review → Rewrite → Diff |


## Memory 

Coming soon







