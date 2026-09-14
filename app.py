import streamlit as st
from google import genai
from google.genai import types

# Set professional branding layout
st.set_page_config(page_title="Apex AI", page_icon="⚙️", layout="centered")

st.title("⚙️ Apex Core Intelligence")
st.caption("Custom Developer Interface | Powered by Gemini 3.6 Flash")

# Initialize persistent session tracking structures
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UPGRADE 1: Iron-Clad Vault Cache to Prevent Multi-Calls ---
@st.cache_resource(show_spinner=False)
def get_gemini_client(api_key):
    # This function isolates the initial handshake so it only runs once per key change
    return genai.Client(api_key=api_key)

# --- UPGRADE 2: Authorization Lock Form ---
# Putting inputs inside a form completely blocks Streamlit from auto-triggering on keypress
with st.sidebar.form("auth_form"):
    st.subheader("🔑 System Access")
    saved_key = st.session_state.get("api_key", "")
    api_input = st.text_input("Authorization Key (API Key):", type="password", value=saved_key)
    submit_btn = st.form_submit_button("Authenticate Engine")
    
    if submit_btn and api_input:
        st.session_state.api_key = api_input
        # Wipe previous session state to clear any errors cleanly
        st.session_state.messages = []
        st.success("Key configuration saved locally!")

# Render Chat History Layout
for msg in st.session_state.messages:
    visual_role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(visual_role):
        st.write(msg["text"])

# Block execution loop if key hasn't been submitted explicitly via form button
if not st.session_state.get("api_key"):
    st.info("System Standby. Paste your developer API key inside the sidebar vault panel and press Authenticate to initialize.")
else:
    # Handle Active Messaging Loop
    if user_input := st.chat_input("Input command or query here..."):
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})

        try:
            with st.spinner("Apex engine computing data logs..."):
                # Call cached client connection seamlessly
                client = get_gemini_client(st.session_state.api_key)
                
                # Reconstruct historical sequence strings cleanly for structural formatting
                history_logs = []
                for m in st.session_state.messages[:-1]:
                    history_logs.append(types.Content(role=m["role"], parts=[types.Part.from_text(text=m["text"])]))
                
                personality_instruction = """
                You are a highly capable, adaptive, and friendly AI collaborator. 
                You speak in a casual, direct, and universal Gen Z tone. Use terms like 'bro' naturally.
                You are a peer, not a strict lecturer. You are an expert in coding assistance, 
                3D modeling concepts, automotive mechanics, fitness advice, and creative hobbies. 
                Keep your sentences relatively short, punchy, and highly scannable.
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
                
                response = chat.send_message(user_input)
            
            with st.chat_message("assistant"):
                st.write(response.text)
            st.session_state.messages.append({"role": "model", "text": response.text})
            
        except Exception as e:
            st.error(f"System Error: {e}")
