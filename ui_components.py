"""
Reusable UI components for the Streamlit chatbot app.
Includes message rendering, file upload section, progress display, and footer.
"""
import streamlit as st
import html
import re
import os
from document_loader import load_document_and_index



def render_file_upload_section(embeddings, faiss_path, text_store_path):
    """
    Render the file upload section with upload functionality.
    """
    st.header("📚 Upload Study Materials")
    # Area to upload files
    uploaded_files = st.file_uploader(
        "Upload class notes (PDFs or PPT/PPTX)", 
        type=["pdf", "pptx", "ppt"],
        accept_multiple_files=True
    )
    # Process uploaded files
    if uploaded_files:
        with st.spinner("Processing documents..."):
            for file in uploaded_files:
                vectorstore = load_document_and_index(file, embeddings, faiss_path)
                if vectorstore:
                    st.session_state.vectorstore = vectorstore
            st.success("Documents uploaded successfully!")



def render_message(content):
    """
    Render message content with proper HTML formatting and sanitization.
    """
    st.markdown(content, unsafe_allow_html=True)



def render_footer():
    """
    Render the fixed footer in the sidebar.
    """
    st.markdown(
        """
        <style>
        .fixed-bottom {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: linear-gradient(90deg, #1E88E5 0%, #1565C0 100%);
            padding: 10px;
            text-align: center;
            color: white;
            z-index: 999;
        }
        </style>
        <div class="fixed-bottom">
            Made with Streamlit + LangChain + Ollama + Hugging Face + FAISS | <a href="https://github.com/Paulina004" style="color: white; text-decoration: underline;">Paulina004</a> on GitHub
        </div>
        """,
        unsafe_allow_html=True
    )



def stream_response(response, message_placeholder):
    """
    Stream a response with HTML support.
    """
    full_response = ""
    # Split by HTML tags to preserve formatting during streaming
    chunks = re.split(r'(<[^>]*>)', response)
    for chunk in chunks:
        if chunk:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
    message_placeholder.markdown(full_response, unsafe_allow_html=True)
    return full_response



def display_learning_progress(learning_progress):
    """
    Display learning progress in the sidebar.
    """
    if learning_progress['topics_covered']:
        st.header("📊 Learning Progress")
        for topic in learning_progress['topics_covered']:
            # Calculate topic understanding percentage
            topic_scores = [
                data.get('score', 0) 
                for q, data in learning_progress['quiz_scores'].items()
                if data['topic'] == topic
            ]
            understanding = (sum(topic_scores) / len(topic_scores)) if topic_scores else 0
            learning_progress['topic_understanding'][topic] = understanding
            # Display topic with progress bar
            st.write(f"**{topic}**")
            st.progress(understanding, text=f"{understanding:.0%} mastery")
    else:
        st.write("No topics covered in quizzes yet. Take a quiz to track your progress!")