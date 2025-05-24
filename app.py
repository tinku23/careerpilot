import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import pycountry
import os
from gtts import gTTS
from io import BytesIO
from fpdf import FPDF

# Page config
st.set_page_config(
    page_title="Compass : AI Career Counselor",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title('🧭 Compass : AI Career Counselor')
st.sidebar.title("Compass : AI Career Counselor")

# Sidebar: Input API key
openai_api_key = st.sidebar.text_input(
    '🔑 Input Your Google Studio Gemini API Key. You can create one [here](https://aistudio.google.com/app/apikey)',
    type="password"
)
st.sidebar.divider()

st.sidebar.markdown("""
👋 Welcome to **Compass: AI Career Counselor** — a smart assistant built using **LangChain**, **Google Gemini**, and **Streamlit**.
🧠 It provides structured, personalized guidance to help you make confident career choices based on your goals and background.
""")

# Get list of countries
country_names = [country.name for country in pycountry.countries]

# Response generation
def generate_response(prompt):
    try:
        os.environ["GOOGLE_API_KEY"] = openai_api_key
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
        )
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        st.error(f"⚠️ Failed to generate response: {str(e)}")
        st.info("Make sure your API key is correct and has access to the Gemini models.")
        return None

# PDF conversion
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf_output = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_output)

# TTS
def generate_audio(text, language_code='en'):
    try:
        tts = gTTS(text=text, lang=language_code)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        st.error(f"🔊 Failed to generate audio: {e}")
        return None

# Language mapping
lang_codes = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "Chinese": "zh-CN",
    "French": "fr"
}

# Input form
response_text = None  # So we can use it outside the form too
with st.form('Form1'):
    career_goal = st.text_area('`1` Tell us what you want to become')
    economic_status = st.selectbox('`2` To better assist, let us know your economic background', ['Poor', 'Middle', 'Rich'], key=1)
    current_class = st.slider(label='`3` What class/standard are you studying in?', min_value=0, max_value=30, key=2)
    nationality = st.selectbox('`4` Select your nationality (for region-specific guidance)', country_names, key=3)
    language = st.selectbox('`5` Select your language (for personalized content)', list(lang_codes.keys()), key=4)
    age = st.slider(label='`6` Select your age (for age-appropriate suggestions)', min_value=0, max_value=100, key=5)
    uploaded_file = st.file_uploader("📄 Optionally upload your report card/resume (PDF/DOC)", type=["pdf", "doc", "docx"])
    submitted = st.form_submit_button('Submit')

    if submitted:
        if not openai_api_key:
            st.warning('⚠ Please enter your Gemini API Key in the sidebar.', icon='⚠')
        elif not career_goal.strip():
            st.warning("⚠ Please enter your career goal.")
        else:
            file_note = f"A report/resume file is uploaded." if uploaded_file else "No additional file provided."
            prompt = (
                f"You are an expert in career counseling. Give a structured career map in {language} language. "
                f"For every step, give online links or resources originating from {nationality} to help the student. "
                f"I am an economically {economic_status} person from {nationality}. I am {age} years old and currently studying in class {current_class}. "
                f"I want to become a {career_goal} in {nationality}. "
                f"{file_note}"
            )
            response_text = generate_response(prompt)

# Handle response outside the form
if response_text:
    st.success("🎯 Here's your personalized career path:")
    st.markdown(response_text)

    # PDF Download
    pdf_file = create_pdf(response_text)
    st.download_button(
        label="📄 Download Career Roadmap as PDF",
        data=pdf_file,
        file_name="career_roadmap.pdf",
        mime="application/pdf"
    )

    # TTS
    lang_code = lang_codes[language]
    audio_data = generate_audio(response_text, language_code=lang_code)
    if audio_data:
        st.audio(audio_data, format='audio/mp3', start_time=0)
