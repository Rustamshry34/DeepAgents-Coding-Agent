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
  cd deepagents-coding```

Install
```bash
  python -m venv .venv && source .venv/bin/activate  # Win: .venv\Scripts\activate
  pip install -r requirements.txt```
