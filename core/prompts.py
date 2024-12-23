# Prompt
router_instructions = """You are an expert at routing a user question to a vectorstore or web search.

The vectorstore contains documents related to the Ottoman Empire.

Use the vectorstore for questions on these topics. For all else, and especially for current events, use web-search.

Return JSON with single key, datasource, that is 'websearch' or 'vectorstore' depending on the question."""

### Retrieval Grader

# Doc grader instructions
doc_grader_instructions = """You are a grader assessing relevance of a retrieved document to a user question.

If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant."""

# Grader prompt
doc_grader_prompt = """Here is the retrieved document: \n\n {document} \n\n Here is the user question: \n\n {question}. 

This carefully and objectively assess whether the document contains at least some information that is relevant to the question.

Return JSON with single key, binary_score, that is 'yes' or 'no' score to indicate whether the document contains at least some information that is relevant to the question."""

### Generate

# Prompt
rag_prompt = """You are an assistant for question-answering tasks. 

Here is the context to use to answer the question:

{context} 

Think carefully about the above context. 

Now, review the user question:

{question}

Provide an answer to this questions using only the above context. 

Use three sentences maximum and keep the answer concise.

Answer:"""

### Hallucination Grader

# Hallucination grader instructions
hallucination_grader_instructions = """

You are a teacher grading a quiz. 

You will be given FACTS and a STUDENT ANSWER. 

Here is the grade criteria to follow:

(1) Ensure the STUDENT ANSWER is grounded in the FACTS. 

(2) Ensure the STUDENT ANSWER does not contain "hallucinated" information outside the scope of the FACTS.

Score:

A score of yes means that the student's answer meets all of the criteria. This is the highest (best) score. 

A score of no means that the student's answer does not meet all of the criteria. This is the lowest possible score you can give.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 

Avoid simply stating the correct answer at the outset."""

# Grader prompt
hallucination_grader_prompt = """FACTS: \n\n {documents} \n\n STUDENT ANSWER: {generation}. 

Return JSON with two two keys, binary_score is 'yes' or 'no' score to indicate whether the STUDENT ANSWER is grounded in the FACTS. And a key, explanation, that contains an explanation of the score."""

### Answer Grader

# Answer grader instructions
answer_grader_instructions = """You are a teacher grading a quiz. 

You will be given a QUESTION and a STUDENT ANSWER. 

Here is the grade criteria to follow:

(1) The STUDENT ANSWER helps to answer the QUESTION

Score:

A score of yes means that the student's answer meets all of the criteria. This is the highest (best) score. 

The student can receive a score of yes if the answer contains extra information that is not explicitly asked for in the question.

A score of no means that the student's answer does not meet all of the criteria. This is the lowest possible score you can give.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 

Avoid simply stating the correct answer at the outset."""

# Grader prompt
answer_grader_prompt = """QUESTION: \n\n {question} \n\n STUDENT ANSWER: {generation}. 

Return JSON with two two keys, binary_score is 'yes' or 'no' score to indicate whether the STUDENT ANSWER meets the criteria. And a key, explanation, that contains an explanation of the score."""

# Answer refiner
answer_refiner_instructions = """You are an expert at improving answers based on feedback.

You will be given:
- The original question
- The original answer
- A grader's feedback explaining whether the answer met the criteria
- The source documents

Your task is to create an improved answer that meets the following criteria:

(1) Addresses any issues identified in the grader's feedback
(2) Remains grounded in the provided source documents
(3) Maintains conciseness (maximum of three sentences)
(4) Directly answers the original question

Focus on:
- Removing any information not supported by the documents
- Adding relevant information that was missed
- Improving clarity and directness
- Maintaining accuracy

If you cannot answer the question, please provide a detailed explanation as to why.

Provide the improved answer only, without additional commentary."""

answer_refiner_prompt = """QUESTION:

{question}

ORIGINAL ANSWER:
{generation}

GRADER FEEDBACK:
{grader_explanation}

SOURCE DOCUMENTS:
{documents}

Based on the grader feedback, provide an improved answer that addresses the issues stated in the feedback while staying grounded in the source documents.

It must answer the original question.

Use three sentences maximum and keep the answer concise.

If you cannot answer the question, please give a detailed explanation as to why.

Improved Answer:"""

def format_docs(docs):
    formatted_docs = []
    for doc in docs:
        formatted_docs.append(doc.page_content)
    return "\n".join(formatted_docs)

__all__ = [name for name in globals() if not name.startswith('__')]