"""
Initializes and configures language models and embedding models for the chatbot.
Handles model loading and error reporting.
"""
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
import streamlit as st



def init_embeddings(model_name='all-MiniLM-L6-v2'):
    """Initialize embeddings model with error handling"""
    try:
        return HuggingFaceEmbeddings(model_name=model_name)
    except Exception as e:
        st.error(f"Failed to initialize embeddings model. Error details: {str(e)}")
        st.info("Please make sure you have an internet connection and the model is accessible.")
        st.stop()



def init_llm(model_name="llama3", temperature=0.7):
    """Initialize LLM with error handling and configurable parameters"""
    try:
        return OllamaLLM(model=model_name, temperature=temperature)
    except Exception as e:
        st.error(f"Failed to initialize Ollama. Please make sure Ollama is running and the model is pulled.")
        st.error(f"Error details: {str(e)}")
        st.info(f"Try running 'ollama pull {model_name}' in your terminal if you haven't already.")
        st.stop()