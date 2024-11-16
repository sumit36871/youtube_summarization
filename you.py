import streamlit as st
from langchain_community.chat_models import ChatOpenAI  # Updated import
from langchain_community.llms import OpenAI  # Updated import
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from pytube import YouTube
from deep_translator import GoogleTranslator
from fpdf import FPDF
import tempfile
import yt_dlp

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the ChatGroq model
model = ChatGroq(
    model="Gemma2-9b-It",  # Use the model of your choice
    groq_api_key=groq_api_key  # Only the Groq API key is required here
)

# Streamlit UI configuration
st.set_page_config(page_title="YouTube Video Summary Chatbot")
st.header("👋👋 I am your chatbot 💬, Paste a YouTube link to get a summary ❓ ")

# Initialize session state for messages if it doesn't exist
if 'mymessages' not in st.session_state:
    st.session_state['mymessages'] = [
        SystemMessage(content="You are a chatbot that summarizes YouTube videos.")
    ]

# Available languages for translation
LANGUAGES = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Chinese': 'zh',
    'Hindi': 'hi'
}


def extract_video_info(video_url):
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Don't download, just extract metadata
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            title = info_dict.get('title', 'No Title')
            description = info_dict.get('description', 'No Description')
            return f"Title: {title}\nDescription: {description}"
    except Exception as e:
        return f"Error extracting video info: {str(e)}"

def translate_text(text, target_lang):
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        return f"Translation error: {str(e)}"

def create_pdf(title, summary, language):
    pdf = FPDF()
    pdf.add_page()
    
    # Set font for non-ascii languages
    if language in ['ja', 'ko', 'zh']:
        pdf.add_font('NotoSansJP', '', 'NotoSansJP-Regular.ttf', uni=True)
        pdf.set_font('NotoSansJP', '', 12)
    else:
        pdf.set_font('Arial', '', 12)
    
    # Add title
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)
    
    # Ensure the summary text is encoded properly and avoid 'latin-1' encoding errors
    pdf.multi_cell(0, 10, summary.encode('latin-1', 'ignore').decode('latin-1'))  # 'ignore' will ignore characters that can't be encoded
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name
    
    # Open file in UTF-8 encoding to handle special characters
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write("Some text with special characters: é, ü, ç")


# Streamlit UI
st.sidebar.header("Options")
target_language = st.sidebar.selectbox("Select Translation Language", list(LANGUAGES.keys()))

# Initialize the session state key for 'input'
if 'input' not in st.session_state:
    st.session_state['input'] = ""

# Input field for user question
input_question = st.text_input("Paste YouTube Video URL: ", key="input")

# Submit button
submit_button = st.button("Get Summary 🙋❓")

# If ask button is clicked
if submit_button and input_question:
    # Extract video info from the provided YouTube URL
    video_info = extract_video_info(input_question)
    
    if "Error" not in video_info:
        # Get summary
        summary_response = model.invoke([{"role": "user", "content": f"Please provide a detailed summary of this video: {video_info}"}])
        original_summary = summary_response.content
        
        # Display original summary
        st.subheader("Original Summary: 👇")
        st.write(original_summary)
        
        # Translate summary if language is not English
        if target_language != 'English':
            translated_summary = translate_text(original_summary, LANGUAGES[target_language])
            st.subheader(f"Translated Summary ({target_language}): 👇")
            st.write(translated_summary)
            
            # Create PDF with both versions
            pdf_path = create_pdf(
                "YouTube Video Summary",
                f"Original Summary:\n\n{original_summary}\n\n{target_language} Translation:\n\n{translated_summary}",
                LANGUAGES[target_language]
            )
        else:
            # Create PDF with only English version
            pdf_path = create_pdf(
                "YouTube Video Summary",
                f"Summary:\n\n{original_summary}",
                'en'
            )
        
        # Add download button for PDF
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Download Summary as PDF",
                data=pdf_file,
                file_name="video_summary.pdf",
                mime="application/pdf"
            )
            
        # Clean up temporary PDF file
        os.unlink(pdf_path)
    else:
        st.warning(video_info)
elif submit_button:
    st.warning("Please enter a YouTube link before submitting.")