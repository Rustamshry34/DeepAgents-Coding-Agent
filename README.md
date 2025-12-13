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



## Fixed Issue

This version includes a fix for the issue where simple queries (like "Hi, how are you?") would show nothing in the UI. The problem was in the streaming response handling - when simple queries don't generate proper streaming events, the UI now falls back to direct invocation and handles various response formats.

## Setup Requirements

1. Make sure you have Ollama running with a model (e.g., qwen3:0.6b) available
2. Install requirements: `pip install -r requirements.txt`
3. Install langchain_ollama: `pip install langchain_ollama`
4. Set up your Tavily API key as an environment variable: `TAVILY_API_KEY=your_key_here`

## Running the Application

```bash
streamlit run app.py
```
