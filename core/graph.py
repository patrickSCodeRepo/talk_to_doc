from langgraph.graph import StateGraph, END
from core.functions import *
from typing_extensions import TypedDict
from typing import List

class GraphState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """

    question: str  # User question
    generation: str  # LLM generation
    updated_generation: str # LLM tried to generate again
    failed_docs: int # Number of failed docs
    max_loops: int  # Max loops for document retrevial
    answers: int  # Number of answers generated
    loop_step: int # Times regenerate has looped
    documents: List[str]  # List of retrieved documents
    bad_explanation: str # Explanation of why the answer was bad
    decision: str # Final decision
    final_answer: str #Final answer

# Initialize the workflow
workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generate
workflow.add_node("grade_answer", grade_generation_v_documents_and_question) # grade answer
workflow.add_node("regenerate_answer", regenerate_answer)
workflow.add_node("finalize", finalize)  # finalize

# Build graph
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")

workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "retrieve_again": "retrieve",
        "generate": "generate",
        "finalize": "finalize",
    },
)

workflow.add_edge("generate", "grade_answer")
workflow.add_edge("grade_answer", "regenerate_answer")
workflow.add_edge("regenerate_answer", "finalize")



# Compile
graph = workflow.compile()

__all__ = [name for name in globals() if not name.startswith('__')]