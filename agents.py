import os
import json
import re
from tavily import TavilyClient
from llm import get_llm, ask

llm = get_llm()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def planner(topic):
    prompt = f"""You are a research planner.
Break this topic into 3 focused, distinct research questions.
Topic: {topic}

Return ONLY a JSON list of strings. No explanation, no markdown."""

    raw = ask(llm, prompt)
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        questions = json.loads(raw)
    except json.JSONDecodeError:
        questions = [topic]

    return questions


def researcher(questions, topic=""):
    sources = []
    seen = set()

    for q in questions:
        if not isinstance(q, str) or len(q.strip()) < 15:
            print("Skipped:", q)
            continue

        query = f"{topic}: {q}"

        try:
            results = tavily.search(query=query, max_results=3)["results"]
        except Exception as e:
            print("Search failed:", e)
            continue

        for r in results:
            if r["url"] in seen:
                continue
            seen.add(r["url"])
            sources.append({
                "id": len(sources) + 1,
                "title": r["title"],
                "url": r["url"],
                "content": r["content"],
            })

    return sources

def writer(topic, sources, feedback="", old_report=""):
    source_text = ""
    for s in sources:
        source_text += f"[{s['id']}] {s['title']} ({s['url']})\n{s['content']}\n\n"

    revision_note = ""
    if feedback and "APPROVED" not in feedback:
        revision_note = f"""
Your previous draft:
{old_report}

Reviewer feedback. Fix these issues:
{feedback}
"""

    prompt = f"""You are a research report writer.
Write a well-structured markdown report on: {topic}

Rules:
- Use ONLY the information from the sources below. Do not add outside facts.
- After every claim, add a citation like [1] or [2].
- Structure: Title, Summary, 3 sections, Conclusion.
- If the sources do not cover something, say so. Do not guess.
{revision_note}
SOURCES:
{source_text}"""

    return ask(llm, prompt)

def critic(report, sources):
    source_text = ""
    for s in sources:
        source_text += f"[{s['id']}] {s['title']}\n{s['content']}\n\n"

    prompt = f"""You are a strict research reviewer.
Check the REPORT against the SOURCES.

Look for:
1. Claims that have no citation
2. Claims that are NOT supported by the cited source
3. Important missing parts

If the report is good, reply with exactly one word: APPROVED
Otherwise reply with a short bullet list of specific fixes.

REPORT:
{report}

SOURCES:
{source_text}"""

    return ask(llm, prompt)