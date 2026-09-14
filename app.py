import streamlit as st
from google import genai
from google.genai import types
from streamlit_lottie import st_lottie
import requests

# Set professional branding layout
st.set_page_config(page_title="Apex AI", page_icon="⚙️", layout="centered")

# Helper function to fetch clean animations safely
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load a premium dark-themed mechanical loading pulse animation
lottie_robot = load_lottieurl("https://lottiefiles.com")

# Header Layout with Side-by-Side Animation Display
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("⚙️ Apex Core Intelligence")
    st.caption("Custom Developer Interface | Powered by Gemini 3.6 Flash")
with col2:
    if lottie_robot:
        st_lottie(lottie_robot, speed=1, reverse=False, loop=True, quality="low", height=80, key="header_bot")

# Authorization Section
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_input = st.text_input("Enter Developer Authorization Key (API Key):", type="password", value=st.session_state.api_key)

if api_input:
    st.session_state.api_key = api_input

# Initialize persistent tracking sessions
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# Render Chat History layout
for msg in st.session_state.messages:
    visual_role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(visual_role):
        st.write(msg["text"])

# Block execution core loop if unauthorized
if not st.session_state.api_key:
    st.info("System Initialized. Please insert an active API key above to unlock the chat engine command bar.")
else:
    if st.session_state.chat_session is None:
        try:
            client = genai.Client(api_key=st.session_state.api_key)
            
            personality_instruction = """
            You are a highly capable, adaptive, and friendly AI collaborator. 
            You speak in a casual, direct, and universal Gen Z tone. Use terms like 'bro' naturally.
            You are a peer, not a strict lecturer. You are an expert in coding assistance, 
            3D modeling concepts, automotive mechanics, fitness advice, and creative hobbies. 
            Keep your sentences relatively short, punchy, and highly scannable.
            Do not use any emojis or complex mathematical symbols in your responses.
            """
            
            st.session_state.chat_session = client.chats.create(
                model="gemini-3.6-flash",
                config=types.GenerateContentConfig(
                    system_instruction=personality_instruction,
                    temperature=0.7,
                )
            )
        except Exception as e:
            st.error(f"Initialization Failure: {e}")
            st.stop()

    # Handle Active Messaging Loop
    if user_input := st.chat_input("Input command or query here..."):
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})

        # Process response wrapped inside a visual loading animation spinner
        try:
            with st.spinner("Apex engine computing data logs..."):
                response = st.session_state.chat_session.send_message(user_input)
            
            with st.chat_message("assistant"):
                st.write(response.text)
            st.session_state.messages.append({"role": "model", "text": response.text})
            
        except Exception as e:
            st.error(f"System Error: {e}")
