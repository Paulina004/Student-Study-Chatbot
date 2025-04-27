# 📘 SoloMind: Study Companion Chatbot

A modern, interactive chatbot designed to help students study smarter using their own course materials. Upload your class notes (PDFs or PowerPoint files), ask questions, generate summaries, and take quizzes—all powered by local language models and vector search.

## Table of Contents

- [🎬 Demo](#-demo)
- [❓ Why Use Study Companion Chatbot Instead of ChatGPT or Online Competitors?](#-why-use-study-companion-chatbot-instead-of-chatgpt-or-online-competitors)
- [✨ Features](#-features)
- [⚙️ Installation Instructions](#-installation-instructions)
- [🔧 Configuration](#-configuration)
- [🚀 Running the Application](#-running-the-application)
- [💡 Usage Examples](#-usage-examples)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [⚠️ Known Limitations](#-known-limitations)
- [📝 Additional Notes](#-additional-notes)

## 🎬 Demo

Check out a video demo of the Chatbot in action:  
[![Watch the demo](https://img.youtube.com/vi/rj0F65ZWhs0/0.jpg)](https://youtu.be/rj0F65ZWhs0)

Or copy the link if the above embed doesn't work: [https://youtu.be/rj0F65ZWhs0](https://youtu.be/rj0F65ZWhs0)

---

## ❓ Why Use Study Companion Chatbot Instead of ChatGPT or Online Competitors?

- **🔒 100% Local & Private:** Your notes never leave your computer—no cloud uploads, no data mining, no tracking.
- **📚 Personalized Answers:** Responses are grounded in your actual course materials, not generic web data. Fights hallucinations and irrelevant content.
- **📝 Transparent Citations:** Every answer is cited with the exact page or slide from your materials, so you can easily verify and review. All answers and summaries include a "References" section for traceability.
- **🧠 Active Learning:** Instantly generate custom quizzes and track your progress—features tailored for students, not just conversation.
- **⚡ Works Offline:** No internet required after setup. No usage limits, subscriptions, or throttling.
- **🛠️ Open & Extensible:** Fully open-source and customizable. Change your model and embedding model as you wish.
- **🎓 Student-Focused:** Built for learning—summarization, Q&A, and quizzes are designed for academic success, not just chat.

---

## ✨ Features

- [x] Upload PDFs and PPT/PPTX files for course notes and slides.
- [x] Get detailed, cited answers from your files thanks to local vector embeddings (FAISS) to retrieve the most relevant content for your queries.
- [x] Generate concise summaries of any topic in your files.
- [x] Create and take multiple-choice quizzes with instant grading and feedback.
- [x] Track your learning progress and quiz history on the website's sidebar.
- [x] Modern, user-friendly Streamlit website interface.
- [x] Fully open-source and model customizable.

---

## ⚙️ Installation Instructions

### Prerequisites

- **Python 3.9+** (recommended: 3.10 or 3.11)
- **[Ollama](https://ollama.com/)** (for running local LLMs, e.g., qwen2.5:14b)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/study-companion-chatbot.git
cd study-companion-chatbot
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Start Ollama

- [Download and install Ollama](https://ollama.com/download)
- Pull the suggested model (e.g., qwen2.5:14b):

```bash
ollama pull qwen2.5:14b
ollama serve  # If not started automatically
```

---

## 🔧 Configuration

- **No environment variables are strictly required for local use.**
- By default, all uploaded files and vector indices are stored in a local `data/` directory.
- If you wish to change the model or embedding backend, edit the `init_llm` and `init_embeddings` functions in `models.py`.

---

## 🚀 Running the Application

From the project root directory, run:

```bash
streamlit run app.py
```

- The app will open in your default web browser using localhost.
- Upload your study materials using the sidebar, then interact with the chatbot in the main window.

---

### 🧪 Testing with Sample Course Materials

You can test the Study Companion Chatbot using the sample files provided in the `course-materials-for-testing` directory. These include a variety of PDFs and PowerPoint presentations (PPT/PPTX) that are ideal for trying out the app's features such as Q&A, summarization, and quiz generation.

The included PowerPoint files are sourced from the publicly available Stanford NLP course materials by Dan Jurafsky and Christopher Manning. You can find the original slides and more resources at the official Stanford NLP Coursera page:
[https://web.stanford.edu/~jurafsky/NLPCourseraSlides.html](https://web.stanford.edu/~jurafsky/NLPCourseraSlides.html)

**How to use for testing:**
- Upload any of the files from `course-materials-for-testing` using the sidebar in the app.
- Try asking questions, requesting summaries, or generating quizzes based on the uploaded content.

---

## 💡 Usage Examples

- **Ask a Question (Default Mode):**  
  Type a question about your uploaded notes, e.g.,  
  _"What is the difference between supervised and unsupervised learning?"_

- **Summarize a Topic:**  
  Click the "Summarize" button, then enter a topic, e.g.,  
  _"Summarize neural networks"_

- **Take a Quiz:**  
  Click the "Quiz" button, enter a topic, and follow the prompts to take a multiple-choice quiz.

- **Track Progress:**  
  View your topic mastery in the sidebar.

---

## 🤝 Contributing

Found a bug? Please open an issue on GitHub or contact [Paulina004](https://github.com/Paulina004) directly.

**Note:** This project is not accepting code contributions at this time.

---

## 📄 License

This project is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License (CC BY-NC-ND 4.0).

**This means you can:**
- Share and redistribute the material
- Give appropriate credit to the original author

**But you cannot:**
- Use the material for commercial purposes 
- Modify or build upon the material
- Distribute modified versions

*For more details, see: https://creativecommons.org/licenses/by-nc-nd/4.0/*

---

## ⚠️ Known Limitations

- **Local-Only:** The app is designed for local use and requires Ollama and FAISS. It does not support cloud-based LLMs or vector stores out of the box.
- **Model Support:** Only models available via Ollama and HuggingFace are supported. You may need to adjust code for other models.
- **File Size:** Large files may slow down processing or exceed memory limits.
- **No User Authentication:** All data is stored locally; there is no user management or cloud sync.
- **Token Limits:** Very large documents or queries may hit LLM context window limits.
- **Reference and Similarity Limitations:** The chatbot uses free/open models for both language and embeddings. Sometimes, the model may make mistakes with references, or the similarity search may not always retrieve the most relevant context. This is a limitation of current free, local open-source models and embedding methods.

---

## 📝 Additional Notes

- **Security:** All processing is local; your documents are never uploaded to a server.
- **Extensibility:** The codebase is modular—add new workflows, models, or UI components as needed.
- **Support:** For issues or questions, please open an issue on GitHub or contact the maintainer, [Paulina004](https://github.com/Paulina004).

---

_Enjoy smarter studying with your own AI-powered class companion!_