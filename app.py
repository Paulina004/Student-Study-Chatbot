"""
Main Streamlit app file for the Study Companion Chatbot.
Handles UI layout, workflow selection, chat interface, and integrates all core modules.
"""
import streamlit as st
import os
import tempfile
from models import init_embeddings, init_llm
from document_loader import load_document_and_index
from workflows import get_workflow, summarize_workflow, quiz_workflow, grade_workflow, qa_workflow
from ui_components import render_message, render_footer, stream_response, display_learning_progress, render_file_upload_section
from session_state import init_session_state, update_quiz_state, update_quiz_score
from defaults import DEFAULT_LLM_MODEL, DEFAULT_LLM_TEMPERATURE, DEFAULT_EMBEDDING_MODEL



# ------------------------------
# Constants
# ------------------------------
DATA_DIR = "data"
FAISS_PATH = os.path.join(DATA_DIR, "vector_index.faiss")
TEXT_STORE_PATH = os.path.join(DATA_DIR, "stored_texts.pkl")
# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR, mode=0o755, exist_ok=True)
    except Exception as e:
        st.error(f"Error creating data directory: {str(e)}")
        st.info("Using temporary directory instead")
        DATA_DIR = tempfile.gettempdir()
        FAISS_PATH = os.path.join(DATA_DIR, "vector_index.faiss")
        TEXT_STORE_PATH = os.path.join(DATA_DIR, "stored_texts.pkl")



# ------------------------------
# Streamlit UI Setup
# ------------------------------
st.set_page_config(page_title="SoloMind", layout="wide")
st.title("📘 Chatbot Workspace")
# Initialize session state and models
init_session_state()
embeddings = init_embeddings(model_name=DEFAULT_EMBEDDING_MODEL)
llm = init_llm(model_name=DEFAULT_LLM_MODEL, temperature=DEFAULT_LLM_TEMPERATURE)



# ------------------------------
# Sidebar UI
# ------------------------------
with st.sidebar:
    st.image(os.path.join("logo", "SoloMind-Logo.png"), width=130)
    # Render file upload section
    render_file_upload_section(embeddings, FAISS_PATH, TEXT_STORE_PATH)
    # --- Workflow Selection Dropdown ---
    st.header("⚙️ Choose Chat Mode")
    chat_modes = ["Default (Q&A)", "Summarize", "Quiz"]
    if 'selected_workflow' not in st.session_state:
        st.session_state.selected_workflow = chat_modes[0]
    selected_mode = st.selectbox("Select using the dropdown menu:", chat_modes, index=chat_modes.index(st.session_state.selected_workflow))
    st.session_state.selected_workflow = selected_mode
    # Display learning progress
    display_learning_progress(st.session_state.learning_progress)
    # Add footer
    render_footer()



# ------------------------------
# Chat Interface
# ------------------------------

# --- Display All Previous Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render_message(message["content"])



# --- Quiz State Handler ---
if st.session_state.selected_workflow == "Quiz":
    quiz_data = st.session_state.learning_progress.get('current_quiz')
    correct_answers = st.session_state.learning_progress.get('quiz_answers', [])
    user_answers = st.session_state.get('user_quiz_answers', [])
    current_index = st.session_state.get('quiz_current_index', 0)

    if quiz_data and current_index < len(quiz_data):
        # Parse the current question and options
        q_text = quiz_data[current_index]
        lines = q_text.split('\n')
        question_line = lines[0]
        options = [l for l in lines[1:] if l.strip().startswith(tuple("ABCD"))]
        st.markdown(f"**{question_line}**")
        answer = st.radio(
            "Choose your answer:",
            options=[opt[:1] for opt in options],  # ['A', 'B', 'C', 'D']
            format_func=lambda x: next((opt for opt in options if opt.startswith(x)), x),
            key=f"quiz_q_{current_index}"
        )
        if st.button("Next", key=f"next_{current_index}"):
            user_answers.append(answer)
            st.session_state['user_quiz_answers'] = user_answers
            st.session_state['quiz_current_index'] = current_index + 1
            st.rerun()
    elif quiz_data and current_index == len(quiz_data):
        # Quiz complete, grade and show feedback
        topic = st.session_state.get("last_quiz_topic", "General")
        score = sum(ua == ca for ua, ca in zip(user_answers, correct_answers)) / len(correct_answers)
        feedback = grade_workflow(quiz_data, user_answers, correct_answers, topic, llm, st.session_state)
        update_quiz_score(topic, score, feedback, user_answers, correct_answers)
        update_quiz_state()  # Reset quiz state
        st.session_state['quiz_current_index'] = 0
        st.session_state['user_quiz_answers'] = []
        response = f"Quiz Complete!<br>Score: {score:.0%}<br><br>{feedback}"
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = stream_response(response, message_placeholder)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        quiz_topic = st.text_input("What topic should I quiz you on?", value=st.session_state.get("last_quiz_topic", ""))
        num_questions = st.selectbox(
            "How many questions would you like?",
            options=[5, 10, 15, 20],
            index=0
        )
        if st.button("Start Quiz"):
            if not quiz_topic.strip():
                st.warning("Please enter a topic for the quiz.")
            elif st.session_state.vectorstore is None:
                st.error("Please upload study materials before starting a quiz!")
            else:
                with st.spinner("Generating quiz questions..."):
                    st.session_state["last_quiz_topic"] = quiz_topic
                    quiz_data = quiz_workflow(quiz_topic, st.session_state.vectorstore, llm, st.session_state, num_questions)
                    update_quiz_state(quiz_data)
                    st.session_state['quiz_current_index'] = 0
                    st.session_state['user_quiz_answers'] = []
                    response = "Let's begin the quiz!"
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = stream_response(response, message_placeholder)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.rerun()

    #st.write("DEBUG: quiz_data = ", quiz_data)



# Ensure quiz_data is always defined before use
quiz_data = st.session_state.learning_progress.get('current_quiz') if 'learning_progress' in st.session_state else None



# --- Main Q&A and Summarize Handler ---
# Hide chat input if quiz is in progress
if not st.session_state.selected_workflow == "Quiz":
    prompt = st.chat_input("Ask a question...")
else:
    prompt = None

if prompt:
    if not st.session_state.vectorstore:
        st.error("Please upload some course materials or notes first!")
        st.stop()
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    # Determine workflow from dropdown selection or fallback
    mode_map = {
        "Default (Q&A)": "default",
        "Summarize": "summarize",
        "Quiz": "quiz"
    }
    workflow = mode_map.get(st.session_state.selected_workflow, get_workflow(prompt))
    # Get bot response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = None
        if workflow == "summarize":
            topic = prompt.replace("summarize", "").replace("summary", "").strip()
            with st.spinner("Generating summary..."):
                response = summarize_workflow(topic, st.session_state.vectorstore, llm, st.session_state)
        # elif workflow == "quiz":
        #     # Store the topic for quiz use
        #     topic = prompt.replace("quiz", "").replace("test me", "").replace("quiz me", "").strip()
        #     st.session_state["last_quiz_topic"] = topic
        #     # The quiz UI will be handled in the quiz state handler above
        #     response = None
        else:
            with st.spinner("Thinking..."):
                response = qa_workflow(prompt, st.session_state.vectorstore, llm)
        if response is not None:
            full_response = stream_response(response, message_placeholder)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
