import streamlit as st
from google import genai
from google.genai import types

# Set professional branding layout up front so it always draws
st.set_page_config(page_title="Apex AI", page_icon="⚙️", layout="centered")
st.title("⚙️ Apex Core Intelligence")
st.caption("Custom Developer Interface | Powered by Gemini 3.6 Flash")

# 1. Provide a dedicated authorization section that doesn't freeze the screen
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Keep key input in an independent visual box
api_input = st.text_input("Enter Developer Authorization Key (API Key):", type="password", value=st.session_state.api_key)

if api_input:
    st.session_state.api_key = api_input

# 2. Maintain Chat History in the web app interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat bubbles on the screen cleanly
for msg in st.session_state.messages:
    visual_role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(visual_role):
        st.write(msg["text"])

# 3. Block only the core execution channel if the key is missing
if not st.session_state.api_key:
    st.info("System Initialized. Please insert an active API key above to unlock the chat engine command bar.")
else:
    # Initialize the Gemini Client safely
    try:
        client = genai.Client(api_key=st.session_state.api_key)
    except Exception as e:
        st.error(f"Initialization Failure: {e}")
        st.stop()

    # Setup the AI's Core Instructions
    personality_instruction = """
    You are a highly capable, adaptive, and friendly AI collaborator. 
    You speak in a casual, direct, and universal Gen Z tone. Use terms like 'bro' naturally.
    You are a peer, not a strict lecturer. You are an expert in coding assistance, 
    3D modeling concepts, automotive mechanics, fitness advice, and creative hobbies. 
    Keep your sentences relatively short, punchy, and highly scannable.
    Do not use any emojis or complex mathematical symbols in your responses.
    """

    # 4. Handle User Input
    if user_input := st.chat_input("Input command or query here..."):
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})

        # Prepare historical context for the API call using strict 'user' and 'model' tags
        history_logs = []
        for m in st.session_state.messages[:-1]:
             history_logs.append(types.Content(role=m["role"], parts=[types.Part.from_text(text=m["text"])]))

        # Trigger the live chat session with historical context
        try:
            chat = client.chats.create(
                model="gemini-3.6-flash",
                history=history_logs,
                config=types.GenerateContentConfig(
                    system_instruction=personality_instruction,
                    temperature=0.7,
                )
            )
            response = chat.send_message(user_input)
            
            with st.chat_message("assistant"):
                st.write(response.text)
            st.session_state.messages.append({"role": "model", "text": response.text})
            
        except Exception as e:
            st.error(f"System Error: {e}")
