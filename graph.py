from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents import planner, researcher, writer, critic

MAX_REVISIONS = 2


class State(TypedDict):
    topic: str
    questions: List[str]
    sources: List[dict]
    report: str
    feedback: str
    revisions: int


def planner_node(state: State):
    print("🧠 Planner is running...")
    return {"questions": planner(state["topic"])}


def researcher_node(state: State):
    print("🔎 Researcher is running...")
    return {"sources": researcher(state["questions"], state["topic"])}


def writer_node(state: State):
    print("✍️  Writer is running...")
    report = writer(
        state["topic"],
        state["sources"],
        feedback=state.get("feedback", ""),
        old_report=state.get("report", ""),
    )
    return {"report": report}


def critic_node(state: State):
    print("🕵️  Critic is running...")
    feedback = critic(state["report"], state["sources"])
    return {"feedback": feedback, "revisions": state["revisions"] + 1}


def should_revise(state: State):
    if "APPROVED" in state["feedback"] or state["revisions"] >= MAX_REVISIONS:
        return END
    print("🔁 Critic found issues, Writer is revising...")
    return "writer"


def build_graph():
    g = StateGraph(State)
    g.add_node("planner", planner_node)
    g.add_node("researcher", researcher_node)
    g.add_node("writer", writer_node)
    g.add_node("critic", critic_node)

    g.set_entry_point("planner")
    g.add_edge("planner", "researcher")
    g.add_edge("researcher", "writer")
    g.add_edge("writer", "critic")
    g.add_conditional_edges("critic", should_revise)

    return g.compile()

