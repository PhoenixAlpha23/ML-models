from langgraph.graph import Graph

workflow = Graph()

# Add nodes
workflow.add_node("extract_transcript", extract_transcript)
workflow.add_node("generate_twitter_thread", generate_twitter_thread)
workflow.add_node("generate_linkedin_post", generate_linkedin_post)

# Define edges (sequential flow)
workflow.add_edge("extract_transcript", "generate_twitter_thread")
workflow.add_edge("generate_twitter_thread", "generate_linkedin_post")

# Conditional error handling
workflow.add_conditional_edges(
    "extract_transcript",
    lambda x: "error" not in x,
    {"True": "generate_twitter_thread", "False": "__end__"}
)

workflow.set_entry_point("extract_transcript")
app = workflow.compile()
