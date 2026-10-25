from graph import build_graph

app = build_graph()

initial_state = {
    "topic": "Impact of AI on healthcare diagnostics",
    "questions": [],
    "sources": [],
    "report": "",
    "feedback": "",
    "revisions": 0,
}

final = app.invoke(initial_state)

print("\n" + "=" * 60)
print(final["report"])
print("=" * 60)
print("Critic's final feedback:", final["feedback"][:200])
print("Total revisions:", final["revisions"])