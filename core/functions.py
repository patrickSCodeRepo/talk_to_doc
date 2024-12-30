import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from core.puller import *
from core.prompts import *

### LLM
local_llm = 'falcon3:7b-instruct-q8_0'
# local_llm = "falcon3:3b-instruct-fp16"
local_llm_hallucinate = "llama3.2:3b-instruct-fp16"
llm = ChatOllama(model=local_llm, temperature=0)
llm_json_mode = ChatOllama(model=local_llm_hallucinate, temperature=0, format="json")

### Nodes
def retrieve(state):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]
    max_loops = state["max_loops"]
    loop_step = state.get("loop_step", 0)
    

    # Write retrieved documents to documents key in state
    documents = retriever.invoke(question)
    return {"documents": documents, "loop_step": loop_step + 1, "max_loops": max_loops}


def generate(state):
    """
    Generate answer using RAG on retrieved documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    docs_txt = format_docs(documents)
    rag_prompt_formatted = rag_prompt.format(context=docs_txt, question=question)
    generation = llm.invoke([HumanMessage(content=rag_prompt_formatted)])

    return {"generation": generation}


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search state
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []

    # Store failed documents
    failed_docs = []

    # Test for amount of documents
    print(len(documents))
    # # Test for document content
    # print(type(documents))
    # for d in documents:
    #     print(d.page_content + "\n\n")


    for d in documents:
        doc_grader_prompt_formatted = doc_grader_prompt.format(
            document=d.page_content, question=question
        )
        result = llm_json_mode.invoke(
            [SystemMessage(content=doc_grader_instructions)]
            + [HumanMessage(content=doc_grader_prompt_formatted)]
        )
        grade = json.loads(result.content)["binary_score"]
        # Document relevant
        if grade.lower() == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        # Document not relevant
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            # We do not include the document in filtered_docs
            # We set a flag to indicate that we want to try again
            failed_docs.append("I")
            continue
    return {"documents": filtered_docs, "failed_docs": len(failed_docs), }

### Edges

def route_question(state):
    """
    Route question to web search or RAG

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    route_question = llm_json_mode.invoke(
        [SystemMessage(content=router_instructions)]
        + [HumanMessage(content=state["question"])]
    )
    source = json.loads(route_question.content)["datasource"]
    if source == "websearch":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "vectorstore"
    elif source == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"


def decide_to_generate(state):
    """
    Determines whether to generate an answer, or add web search

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    max_loops = state["max_loops"]
    question = state["question"]
    filtered_documents = state["documents"]

    failed_docs = state["failed_docs"]
    loop_step = state["loop_step"]

    if loop_step < max_loops:
        if failed_docs > 5:
            # All documents have been filtered check_relevance
            # We will re-generate a new query
            print("---DECISION: NOT ALL DOCUMENTS ARE RELEVANT TO QUESTION, TRYING AGAIN---")
            return "retrieve_again"
        else:
            # We have relevant documents, so generate answer
            print("---DECISION: GENERATE---")
            return "generate"
    else:
        return "finalize"


def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for the next node to call
    """
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    hallucination_grader_prompt_formatted = hallucination_grader_prompt.format(
        documents=format_docs(documents), generation=generation.content
    )
    result = llm_json_mode.invoke(
        [SystemMessage(content=hallucination_grader_instructions)]
        + [HumanMessage(content=hallucination_grader_prompt_formatted)]
    )

    grade = json.loads(result.content)["binary_score"]

    if grade.lower() == "yes":
        print("---DECISION: Generation is grounded in documents---")
        # Check if the generation answers the question
        answer_grader_prompt_formatted = answer_grader_prompt.format(
            question=question, generation=generation.content
        )
        result = llm_json_mode.invoke(
            [SystemMessage(content=answer_grader_instructions)]
            + [HumanMessage(content=answer_grader_prompt_formatted)]
        )
        answer_grade = json.loads(result.content)["binary_score"]
        answer_explanation = json.loads(result.content)["explanation"]

        if answer_grade.lower() == "yes":
            print("---DECISION: Generation addresses the question---")
            return {"decision": "useful"}
        else:
            print("---DECISION: Generation does not address the question, saving off bad explanation---")
            return {"decision": "not useful", "bad_explanation": answer_explanation}

def regenerate_answer(state):
    
    generation = state["generation"]
    
    if state["decision"] == "useful":
        return {"final_answer": generation}
    
    else:
        print("---REGENERATE: Regenerating answer based on fallacy issues---")
        question = state["question"]
        generation = state["generation"].content
        grader_explanation = state["bad_explanation"]
        documents = state["documents"]

        # print(question, "\n", generation, "\n", grader_explanation, "\n", documents, "\n")

        refined_answer = llm.invoke(
            [SystemMessage(content=answer_refiner_instructions)]
            + [HumanMessage(content=answer_refiner_prompt.format(
                question=question,
                generation=generation,
                grader_explanation=grader_explanation,
                documents=documents
            ))]
        )

        return {"final_answer": refined_answer, "decision": "useful"}

def finalize(state):
    """
    Finalizes the response based on the decision.

    Args:
        state (dict): The current graph state

    Returns:
        dict: Contains the final answer to be returned to the user
    """

    max_loops = state["max_loops"]
    decision = state.get("decision")
    final_answer = state.get("final_answer")
    loop_step = state["loop_step"]

    if decision == "useful":
        print("---FINALIZE: Returning the generated answer---")
        return {"final_answer": final_answer}
    
    elif decision == "not useful":
        print("---FINALIZE: Returning answer not useful---")
        not_useful = "The answer I came up with was not good enough"
        return {"final_answer": not_useful}
    
    elif loop_step == max_loops:
        print("---FINALIZE: Returning answer ran out of attempts---")
        fallback_message = "I am unable to provide an answer at this time."
        return {"final_answer": fallback_message}
    
    else:
        print("---FINALIZE: Undefined decision, returning fallback message---")
        fallback_message = "I am unable to provide an answer at this time."
        return {"final_answer": fallback_message}

__all__ = [name for name in globals() if not name.startswith('__')]
