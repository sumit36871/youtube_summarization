import streamlit as st
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_community import chat_models
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from pytube import YouTube

# Load environment variables
load_dotenv()
groq_api_key=os.getenv("GROQ_API_KEY")

# Initialize the ChatOpenAI model
model=ChatGroq(model="Gemma2-9b-It",groq_api_key=groq_api_key)

# Streamlit UI configuration
st.set_page_config(page_title="YouTube Video Summary Chatbot")
st.header("👋👋 I am your chatbot 💬, Paste a YouTube link to get a summary ❓ ")

# Initialize session state for messages if it doesn't exist
if 'mymessages' not in st.session_state:
    st.session_state['mymessages'] = [
        SystemMessage(content="You are a chatbot that summarizes YouTube videos.")
    ]

# Function to extract video details
def extract_video_info(video_url):
    try:
        video = YouTube(video_url)
        title = video.title
        description = video.description
        return f"Title: {title}\nDescription: {description}"
    except Exception as e:
        return f"Error extracting video info: {str(e)}"

# Function to get response from the OpenAI model
def chatmodel_response(question):
    if isinstance(question, str) and question.strip():
        st.session_state['mymessages'].append(HumanMessage(content=question))
        
        # Get the response from the chat model
        response = model.invoke(st.session_state['mymessages'])
        
        # Append the AI response to the messages
        st.session_state['mymessages'].append(AIMessage(content=response.content))
        return response.content
    else:
        return "Please provide a valid question."

# Input field for user question
input_question = st.text_input("Paste YouTube Video URL: ", key="input")

# Submit button
submit_button = st.button("Get Summary 🙋❓")

# If ask button is clicked
if submit_button and input_question:
    # Extract video info from the provided YouTube URL
    video_info = extract_video_info(input_question)
    
    # Check if video info extraction was successful
    if "Error" not in video_info:
        summary = model.invoke([{"role": "user", "content": video_info}])
        st.subheader("This is your Video Summary: 👇")
        st.write(summary.content)
    else:
        st.warning(video_info)
elif submit_button:
    st.warning("Please enter a YouTube link before submitting.")
