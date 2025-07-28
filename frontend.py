#frontend.py
import streamlit as st
st.set_page_config(page_title="GPT Shield", layout="centered")
import time
from agent_runner import run_agentic_task
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import nltk
from nltk.util import ngrams
from nltk.probability import FreqDist
import plotly.express as px
from collections import Counter
from nltk.corpus import stopwords
import string
import json
import os
import bcrypt
from welcome import welcome_screen
from auth import auth_flow

auth_flow()

if not st.session_state.authenticated:
    st.stop()

nltk.download('punkt')
nltk.download('stopwords')

@st.cache_resource
def load_model():
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    return tokenizer, model

tokenizer, model = load_model()

def calculate_perplexity(text):
    encoded_input = tokenizer.encode(text, add_special_tokens=False, return_tensors='pt')
    input_ids = encoded_input[0]
    with torch.no_grad():
        outputs = model(input_ids.unsqueeze(0))
        logits = outputs.logits
    loss = torch.nn.functional.cross_entropy(logits.view(-1, logits.size(-1)), input_ids.view(-1))
    return torch.exp(loss).item()

def calculate_burstiness(text):
    tokens = nltk.word_tokenize(text.lower())
    word_freq = FreqDist(tokens)
    repeated_count = sum(count > 1 for count in word_freq.values())
    return repeated_count / len(word_freq)

def plot_top_repeated_words(text):
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    tokens = [token.lower() for token in tokens if token.lower() not in stop_words and token.lower() not in string.punctuation]
    word_counts = Counter(tokens)
    top_words = word_counts.most_common(10)
    words, counts = zip(*top_words) if top_words else ([], [])
    fig = px.bar(x=words, y=counts, labels={'x': 'Words', 'y': 'Counts'}, title="Top 10 Most Repeated Words")
    st.plotly_chart(fig, use_container_width=True)
    
# Sidebar
agent_mode = st.sidebar.toggle("🧠 Enable Agentic AI", value=True)
st.sidebar.title("🧰 GPT Shield Toolkit")
selected_tool = st.sidebar.radio(
    "Choose a feature:",
    ["AI Content Detection", "Document Analyzer", "AI Rewriter", "Readability & Grammar", "AI Chat Assistant"],
    key="main_tool_selector"
)

if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.show_welcome = True

    st.success("✅ You have been logged out successfully!")
    time.sleep(1)
    st.rerun()


#Theme mode
theme_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)
if theme_mode:
    st.markdown("""
        <style>
        body { background-color: #111; color: white; }
        .stButton>button { background-color: #444; color: white; }
        </style>
    """, unsafe_allow_html=True)

# AI Content Detection (placeholder)
if selected_tool == "AI Content Detection":
    st.header("🛡️ GPT Shield: AI Content Detector")
    with st.expander("📘 What is Perplexity?"):
        st.markdown("""
        Perplexity is a measure of how predictable a text is for a language model.
        - **Low Perplexity**: Model finds the text predictable → could be AI-generated.
        - **High Perplexity**: Text is more complex or less predictable → more likely human-written.
        """)


    text_area = st.text_area("✍️ Enter your text")

    if text_area:
        if st.button("Analyze"):

            if len(text_area.split()) < 20:
                st.warning("⚠️ Please enter at least 20 words for accurate analysis.")
            else:
                # Auto scroll to bottom
                st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 1, 1])

                with col1:
                    st.info("📄 Your Input Text")
                    st.success(text_area)

                with col2:
                    st.info("📊 Calculated Scores")
                    perplexity = calculate_perplexity(text_area)
                    burstiness_score = calculate_burstiness(text_area)

                    st.success(f"Perplexity Score: {perplexity:.2f}")
                    st.success(f"Burstiness Score: {burstiness_score:.2f}")

                    if perplexity > 30000 and burstiness_score < 0.2:
                        st.error("🔍 AI Generated Content Detected")
                    elif 10000 < perplexity <= 30000 or 0.2 <= burstiness_score < 0.4:
                        st.warning("🤖 Possibly AI-Assisted Content")
                    else:
                        st.success("✅ Likely Human-Written Content")

                    # 📥 Download Result Button
                    result = f"""
    GPT Shield - AI Plagiarism Detection Report

    Input:
    {text_area.strip()}

    Perplexity Score: {perplexity:.2f}
    Burstiness Score: {burstiness_score:.2f}

    Result: {"AI Generated" if perplexity > 30000 and burstiness_score < 0.2 else "Possibly AI-Assisted" if 10000 < perplexity <= 30000 or 0.2 <= burstiness_score < 0.4 else "Likely Human-Written"}
    """.strip()

                    st.download_button("📥 Download Report", result, file_name="gpt_shield_report.txt")

                with col3:
                    st.info("📈 Basic Insights")
                    plot_top_repeated_words(text_area)
    # st.info("⚠️ This tool is not affected by Agent Mode.")
    # st.write("Please scroll up to view the full original AI Detection logic.")
    # st.warning("This section is unchanged — review manually if needed.")

# Document Analyzer (placeholder)
elif selected_tool == "Document Analyzer":
    st.header("📄 Document Analyzer")
    st.info("⚠️ This tool is not affected by Agent Mode.")
    st.write("Upload a `.pdf`, `.docx`, or `.txt` file to analyze for AI-generated content.")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

    extracted_text = ""

    if uploaded_file:
        file_type = uploaded_file.type

        if file_type == "text/plain":
            extracted_text = uploaded_file.read().decode("utf-8")

        elif file_type == "application/pdf":
            try:
                import fitz  # PyMuPDF
                with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                    for page in doc:
                        extracted_text += page.get_text()
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                from docx import Document
                doc = Document(uploaded_file)
                extracted_text = "\n".join([para.text for para in doc.paragraphs])
            except Exception as e:
                st.error(f"Error reading DOCX: {e}")

    if extracted_text:
        st.subheader("📃 Extracted Text")
        st.text_area("Text from uploaded file:", value=extracted_text, height=300)

        if st.button("Analyze Document"):
            if len(extracted_text.split()) < 20:
                st.warning("⚠️ The document is too short for reliable analysis.")
            else:
                perplexity = calculate_perplexity(extracted_text)
                burstiness_score = calculate_burstiness(extracted_text)

                st.success(f"Perplexity Score: {perplexity:.2f}")
                st.success(f"Burstiness Score: {burstiness_score:.2f}")

                if perplexity > 30000 and burstiness_score < 0.2:
                    st.error("🔍 AI Generated Content Detected")
                elif 10000 < perplexity <= 30000 or 0.2 <= burstiness_score < 0.4:
                    st.warning("🤖 Possibly AI-Assisted Content")
                else:
                    st.success("✅ Likely Human-Written Content")

                result = f"""
GPT Shield - Document Report

Perplexity Score: {perplexity:.2f}
Burstiness Score: {burstiness_score:.2f}

Result: {"AI Generated" if perplexity > 30000 and burstiness_score < 0.2 else "Possibly AI-Assisted" if 10000 < perplexity <= 30000 or 0.2 <= burstiness_score < 0.4 else "Likely Human-Written"}
""".strip()

                st.download_button("📥 Download Report", result, file_name="document_report.txt")

    st.warning("This section is unchanged — review manually if needed.")

# AI Rewriter
elif selected_tool == "AI Rewriter":
    st.header("✍️ AI Rewriter / Paraphraser")
    
    uploaded_file = st.file_uploader("📤 Upload a `.txt` file (optional)", type=["txt"])
    input_text = ""

    if uploaded_file:
        input_text = uploaded_file.read().decode("utf-8")
        st.text_area("Text from uploaded file:", value=input_text, height=200, key="rewrite_upload_input")
    else:
        input_text = st.text_area("Enter the text you want to rephrase:")

    if st.button("🔄 Rephrase Text"):
        if input_text.strip() == "":
            st.warning("⚠️ Please enter some text.")
        else:
            with st.spinner("Rewriting..."):
                try:
                    if agent_mode:
                        from agent_runner import run_agentic_task
                        prompt = f"Rewrite this text in a formal tone:\n\n{input_text}"
                        rewritten_text = run_agentic_task(prompt)
                    else:
                        import google.generativeai as genai
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(f"Paraphrase this text in natural English:\n\n{input_text}")
                        rewritten_text = response.text.strip()

                    st.success("✅ Rephrased Successfully!")
                    st.text_area("Rewritten Text:", value=rewritten_text, height=200)
                    st.download_button("📥 Download Rewritten Text", rewritten_text, file_name="rewritten_text.txt")

                except Exception as e:
                    st.error(f"⚠️ Failed to rewrite: {e}")

# Readability & Grammar
elif selected_tool == "Readability & Grammar":
    st.header("🧠 Readability & Grammar Analyzer")
    language = st.selectbox("🌐 Choose Language", ["English", "Hindi"])
    input_text = st.text_area("Enter your text for analysis:")

    if st.button("🔍 Analyze Readability & Grammar"):
        if not input_text.strip():
            st.warning("⚠️ Please enter some text.")
        else:
            try:
                import textstat
                import plotly.graph_objs as go
                from gtts import gTTS
                from io import BytesIO
                import base64

                # Readability
                flesch = textstat.flesch_reading_ease(input_text)
                grade_level = textstat.text_standard(input_text)

                st.subheader("📊 Readability Scores")
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=flesch,
                    title={'text': "Flesch Reading Ease"},
                    gauge={'axis': {'range': [0, 100]},
                           'bar': {'color': "blue"},
                           'steps': [
                               {'range': [0, 30], 'color': "red"},
                               {'range': [30, 60], 'color': "orange"},
                               {'range': [60, 100], 'color': "green"}]}))
                st.plotly_chart(fig, use_container_width=True)
                st.success(f"📘 Suggested Grade Level: {grade_level}")

                # Grammar Correction
                if agent_mode:
                    from agent_runner import run_agentic_task
                    prompt = f"Fix grammar and explain corrections:\n\n{input_text}"
                    corrected = run_agentic_task(prompt)
                    st.text_area("Corrected Text (Agent):", value=corrected, height=200)
                else:
                    import language_tool_python
                    tool = language_tool_python.LanguageToolPublicAPI('en-US')
                    matches = tool.check(input_text)
                    corrected = language_tool_python.utils.correct(input_text, matches)

                    #####
                    st.subheader("🔧 Grammar Suggestions")
                    st.info(f"Number of issues detected: {len(matches)}")
                    for match in matches[:5]:
                        st.write(f"• {match.message} (suggestion: `{', '.join(match.replacements)}`)")
                    st.markdown("**✏️ Corrected Version:**")
                    st.text_area("Corrected Text:", value=corrected, height=200)
                    ######

                st.markdown("**🔊 Listen to Corrected Text:**")
                tts = gTTS(corrected, lang="en" if language == "English" else "hi")
                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                b64_audio = base64.b64encode(audio_bytes.read()).decode()
                st.audio(f"data:audio/mp3;base64,{b64_audio}", format="audio/mp3")

            

            except Exception as e:
                st.error(f"⚠️ Grammar analysis failed: {e}")
                
elif selected_tool == "AI Chat Assistant":
    st.header("💬 AI Chat Assistant")
    st.write("Ask anything and get smart responses powered by GPT!")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    uploaded_pdf = st.file_uploader("📤 Upload a PDF to chat about (optional)", type=["pdf"])

    if uploaded_pdf and "pdf_content_loaded" not in st.session_state:
        try:
            import fitz  # PyMuPDF
            with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
                extracted_text = ""
                for page in doc:
                    extracted_text += page.get_text()
            st.session_state.chat_history.append({
                "role": "system",
                "content": f"📘 The user uploaded this document:\n\n{extracted_text[:3000]}...\n\n(Only first 3000 characters shown to keep response concise)"
            })
            st.session_state.pdf_content_loaded = True
            st.success("✅ PDF content loaded into assistant memory.")
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        if "pdf_content_loaded" in st.session_state:
            del st.session_state.pdf_content_loaded

    user_input = st.chat_input("Type your question...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            try:
                full_prompt = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history]) + "\nAssistant:"

                if agent_mode:
                    assistant_reply = run_agentic_task(full_prompt)
                else:
                    import google.generativeai as genai
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(full_prompt)
                    assistant_reply = response.text.strip()

                st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

            except Exception as e:
                st.error(f"❌ Failed to get response: {e}")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                try:
                    from gtts import gTTS
                    from io import BytesIO
                    import base64

                    tts = gTTS(text=msg["content"], lang='en')
                    audio_bytes = BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    b64_audio = base64.b64encode(audio_bytes.read()).decode()
                    st.audio(f"data:audio/mp3;base64,{b64_audio}", format="audio/mp3")
                except Exception as e:
                    st.warning(f"🔊 TTS failed: {e}")
