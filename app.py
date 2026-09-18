import streamlit as st
from google import genai
from google.genai import types

# Set professional layout
st.set_page_config(page_title="Apex AI", page_icon="⚙️", layout="centered")

st.title("⚙️ Apex Core Intelligence")
st.caption("Your personal  AI assistant | Powered by Gemini 3.6 Flash")

# Initialize persistent session tracking structures
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AUTHORIZATION FORM BLOCK ---
# Wrapping this inside a formal container blocks Streamlit from auto-refreshing on every keystroke
with st.sidebar.form("auth_form"):
    st.subheader("🔑 System Access")
    saved_key = st.session_state.get("api_key", "")
    api_input = st.text_input("Authorization Key (API Key):", type="password", value=saved_key)
    submit_btn = st.form_submit_button("start Apex")
    
    if submit_btn and api_input:
        st.session_state.api_key = api_input
        st.session_state.messages = [] # Clear history on fresh token login
        st.success("Apex is ready to go!")

# Render History Blocks Cleanly
for msg in st.session_state.messages:
    visual_role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(visual_role):
        st.write(msg["text"])

# Block execution loop if key hasn't been submitted explicitly via form button
if not st.session_state.get("api_key"):
    st.info("Apex standby, pls enter your API key to start Apex ")
else:
    # --- ISOLATED MESSAGE SUBMISSION BLOCK ---
    # We use a standard text box form here to freeze background requests until you click "Send Command"
    with st.form("message_form", clear_on_submit=True):
        user_input = st.text_input("Input command or query here:", placeholder="Just ask it...")
        send_btn = st.form_submit_button(" ENTER ")

    if send_btn and user_input:
        # Append User text directly to local history cache
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})

        try:
            with st.spinner("Thinking!"):
                # Spawn a standalone client handler cleanly for this query instance
                client = genai.Client(api_key=st.session_state.api_key)
                
                # Format previous history strings matching the strict schema expectations
                history_logs = []
                for m in st.session_state.messages[:-1]:
                    history_logs.append(types.Content(role=m["role"], parts=[types.Part.from_text(text=m["text"])]))
                
                personality_instruction = """
                You are a highly capable, adaptive, and friendly AI collaborator. 
                You speak in a casual, direct, and universal Gen Z tone. Use terms like 'bro' naturally.
                You are a peer, not a strict lecturer. You are an expert in coding assistance, 
                3D modeling concepts, automotive mechanics, fitness advice, and creative hobbies. 
                Keep your sentences relatively as long needed , punchy,motivating,and highly scannable.
                Do not use any emojis or complex mathematical symbols in your responses.
                """
                
                chat = client.chats.create(
                    model="gemini-3.6-flash",
                    history=history_logs,
                    config=types.GenerateContentConfig(
                        system_instruction=personality_instruction,
                        temperature=0.7,
                    )
                )
                
                # Fetch text result strings over the designated active query stream
                response = chat.send_message(user_input)
            
            with st.chat_message("assistant"):
                st.write(response.text)
            st.session_state.messages.append({"role": "model", "text": response.text})
            
            # Force layout execution refresh step to keep visual order crisp
            st.rerun()
            
        except Exception as e:
            st.error(f"System Error: {e}")
