"""
Manages Streamlit session state for chat history, learning progress, quiz state, and vectorstore.
Provides utility functions for state initialization and updates.
"""
import streamlit as st



def init_session_state():
    """
    Initialize all session state variables.
    """
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'learning_progress' not in st.session_state:
        st.session_state.learning_progress = {
            'topics_covered': set(),
            'topic_understanding': {},  # Track understanding per topic
            'current_quiz': None,  # Store current quiz
            'quiz_answers': [],  # Store correct answers for current quiz
            'quiz_scores': {}  # Store quiz scores for each topic
        }
    


def update_quiz_state(quiz_data=None):
    """
    Update quiz-related session state.
    """
    if quiz_data:
        st.session_state.learning_progress['current_quiz'] = quiz_data['questions']
        st.session_state.learning_progress['quiz_answers'] = quiz_data['answers']
    else:
        st.session_state.learning_progress['current_quiz'] = None
        st.session_state.learning_progress['quiz_answers'] = []



def update_quiz_score(topic, score, feedback, user_answers, correct_answers):
    """
    Update quiz scores in session state.
    """
    st.session_state.learning_progress['quiz_scores'][topic] = {
        'score': score,
        'answers': user_answers,
        'correct_answers': correct_answers,
        'topic': topic  
    }
    st.session_state.learning_progress['topics_covered'].add(topic)