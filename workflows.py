"""
Implements core chatbot workflows: Q&A (default), summarization, quiz generation, and grading.
Handles prompt construction, context retrieval, and workflow logic.
"""
import re
from prompts import qa_prompt, summarize_prompt, quiz_prompt, grade_prompt
from rich.console import Console
from rich.panel import Panel
from rich.text import Text



# Initialize rich console
console = Console()



def log_final_prompt(chain, **kwargs):
    """
    Log the actual final prompt that will be sent to the model chain (for debugging purposes).
    """
    try:
        if hasattr(chain, 'steps'):
            prompt_template = chain.steps[0]
            if hasattr(prompt_template, 'prompt'):
                prompt_template = prompt_template.prompt
            try:
                final_prompt = prompt_template.format(**kwargs)
            except:
                final_prompt = str(prompt_template)
        else:
            final_prompt = chain.prompt.format(**kwargs)
        text = Text()
        text.append("🤖 Final Prompt to Model\n", style="bold green")
        text.append(final_prompt, style="yellow")
        console.print(Panel(text, border_style="red"))
    except Exception as e:
        console.print(f"[yellow]Unable to display full prompt: {str(e)}[/yellow]")
        console.print(f"[yellow]Chain type: {type(chain)}[/yellow]")



def format_source_reference(doc):
    """
    Format source reference based on document type.
    """
    try:
        metadata = doc.metadata
        if not metadata:
            return "(Source information unavailable)"
        source = metadata.get('source', 'Unknown Source')
        # Check if the document is a PowerPoint slide
        if metadata.get("type") == "slide":
            slide_num = metadata.get('slide_number', '?')
            slide_title = metadata.get('slide_title', 'Untitled')
            return f"[From Slide {slide_num} in {source}: \"{slide_title}\"]" if slide_title != "Untitled" else f"[From Slide {slide_num} in {source}]"
        # Else, the document is a PDF page
        else:
            page_num = metadata.get('page_number', '?')
            return f"[From Page {page_num} in {source}]"
    except AttributeError:
        return "(Source information unavailable)"



def get_context_from_docs(docs, topic=None):
    """
    Get formatted context from documents with source references.
    """
    context_parts = []
    for doc in docs:
        source_ref = format_source_reference(doc)
        # Add a newline before the source reference for better readability
        context_parts.append(f"{doc.page_content}\n{source_ref}\n---\n")
    return "\n\n".join(context_parts)



def execute_chain(chain, llm, **kwargs):
    """
    Execute a chain with prompt logging.
    """
    log_final_prompt(chain, **kwargs)
    return chain.invoke(kwargs)



def get_workflow(question):
    """
    Determine the workflow type based on the question.
    This is a fallback in case the user doesn't specify the workflow by clicking the UI buttons.
    """
    q_lower = question.lower()
    if any(term in q_lower for term in ["summarize", "summary"]):
        return "summarize"
    elif any(term in q_lower for term in ["quiz", "test me", "quiz me"]):
        return "quiz"
    return "default"



def qa_workflow(question, vectorstore, llm):
    """
    Generate a response to the question using the qa prompt.
    """
    # Get relevant documents using key terms
    key_terms = re.findall(r'\b\w+\b', question.lower())
    docs = vectorstore.similarity_search(" ".join(key_terms), k=10)
    context = get_context_from_docs(docs)
    # Generate response
    chain = qa_prompt | llm
    return execute_chain(chain, llm, 
        context=context, 
        question=question
    ) 



def summarize_workflow(topic, vectorstore, llm, session_state):
    """
    Summarize the topic using the summarize prompt.
    """
    # Get relevant documents and context
    docs = vectorstore.similarity_search(topic, k=10)
    context = get_context_from_docs(docs)
    # Generate summary
    chain = summarize_prompt | llm
    return execute_chain(chain, llm, 
        context=context, 
        topic=topic
    )



def quiz_workflow(topic, vectorstore, llm, session_state, num_questions=5):
    """
    Generate a quiz based on the topic using the quiz prompt.
    """
    # Get relevant documents and context
    docs = vectorstore.similarity_search(topic, k=10)
    context = get_context_from_docs(docs)
    # Get previous questions to avoid repetition
    previous_questions = "\n".join([
        q for q, data in session_state.learning_progress.get('quiz_scores', {}).items()
        if topic.lower() in q.lower()
    ])
    # Generate quiz
    chain = quiz_prompt | llm
    quiz_response = execute_chain(chain, llm,
        context=context,
        topic=topic,
        num_questions=num_questions,
        previous_questions=previous_questions
    )
    print("DEBUG: quiz_response:", quiz_response)
    return parse_quiz_response(quiz_response)



def parse_quiz_response(quiz_response):
    """
    Parse the quiz response into questions, answers, and formatted display.
    Expects each question to start with 'Question X:' and the answer to be marked with 'ANSWER:'.
    """
    questions = []
    answers = []
    formatted_quiz = ""
    current_question = ""
    for line in quiz_response.split('\n'):
        line = line.strip()
        if re.match(r"^Question \d+:", line):
            if current_question:
                questions.append(current_question.strip())
            current_question = line
        elif re.match(r"^[A-D]\)", line):
            current_question += "\n" + line
        elif "ANSWER:" in line:
            answer = line.split("ANSWER:")[-1].strip()
            answers.append(answer)
    if current_question:
        questions.append(current_question.strip())

    formatted_quiz = ""
    for q in questions:
        formatted_quiz += f"{q}\n\n"
    return {
        'questions': questions,
        'answers': answers,
        'formatted_quiz': formatted_quiz.strip()
    }



def grade_workflow(questions, user_answers, correct_answers, topic, llm, session_state):
    """
    Grade the quiz using the grade prompt.
    """
    # Prepare results
    results = [
        f"Q{i}: {'✓' if ua == ca else '✗'} - You answered {ua}, Correct: {ca}"
        for i, (ua, ca) in enumerate(zip(user_answers, correct_answers), 1)
    ]
    # Get student progress
    student_progress = {
        "topics": list(session_state.learning_progress['topics_covered']),
        "quiz_history": len(session_state.learning_progress['quiz_scores']),
        "current_topic_attempts": sum(
            1 for q, data in session_state.learning_progress['quiz_scores'].items()
            if data['topic'] == topic
        )
    }
    # Get formatted quiz string
    if isinstance(questions, dict):
        formatted_quiz = questions.get('formatted_quiz', '')
    elif isinstance(questions, list) and len(questions) > 0 and isinstance(questions[0], str):
        formatted_quiz = "\n\n".join(questions)
    else:
        formatted_quiz = ""
    # Generate feedback
    chain = grade_prompt | llm
    return execute_chain(chain, llm,
        results="\n".join(results),
        topic=topic,
        student_progress=student_progress,
        formatted_quiz=formatted_quiz
    )