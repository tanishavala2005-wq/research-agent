# Multi-Agent Research Assistant

Give a topic. Four AI agents collaborate to research it and write a cited report.

**Live demo:** https://research-agent-jkt3.onrender.com/

## How it works

Topic -> Planner -> Researcher -> Writer -> Critic
If the Critic finds issues, the report goes back to the Writer (max 2 revisions).

| Agent | Role |
|---|---|
| Planner | Breaks the topic into focused research questions |
| Researcher | Searches the web (Tavily) and collects sources |
| Writer | Writes a report using ONLY the retrieved sources, with citations |
| Critic | Fact-checks the draft; sends it back to the Writer if issues are found |

The Critic to Writer feedback loop is built with LangGraph.

## Features

- Conditional feedback loop between Critic and Writer
- Citation-grounded writing to reduce hallucination
- Live agent progress with per-agent timing
- Agent trace, sources list, PDF and Markdown export
- Animated 3D UI built with Streamlit and three.js

## Tech stack

Python, LangGraph, LangChain, Gemini API, Tavily Search, Streamlit, fpdf2

## Run locally

```
git clone https://github.com/tanishavala2005-wq/research-agent.git
cd research-agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, add your own API keys, then run:

```
streamlit run app.py
```

## Project structure

- agents.py: Planner, Researcher, Writer, Critic
- graph.py: LangGraph workflow and revision loop
- llm.py: Gemini setup
- app.py: Streamlit UI
- pdf_export.py: PDF generation

## Future work

Parallel researchers, source credibility scoring, report quality evaluation, multi-LLM comparison.
