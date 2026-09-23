import streamlit as st
from google import genai
from google.genai import types
from io import BytesIO
from PIL import Image

# Initialize space mission configurations
st.set_page_config(page_title="Apex Space Core", page_icon="🌌", layout="centered")

# --- HIGH-TECH SPACE STYLING (CSS INJECTION) ---
st.markdown("""
<style>
    /* Deep space cosmic gradient background */
    .stApp {
        background: linear-gradient(135deg, #060814 0%, #0b112c 50%, #1a0b2e 100%) !important;
        color: #e0e6ed !important;
    }
    
    /* Neon glow effect for main headers and container outlines */
    h1 {
        color: #00f2fe !important;
        text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
        font-family: 'Courier New', Courier, monospace;
    }
    
    .stCaption {
        color: #9fa8da !important;
    }
    
    /* Cyber styling for input fields */
    input {
        background-color: #0d153a !important;
        border: 1px solid #00f2fe !important;
        color: #ffffff !important;
        box-shadow: 0 0 5px rgba(0, 242, 254, 0.3);
    }
    
    /* Custom spacing loops for side graphics */
    .space-banner {
        border-radius: 12px;
        box-shadow: 0 0 15px #7f00ff;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Layout Split for Space Graphic
col1, col2 = st.columns([0.7, 0.3])
with col1:
    st.title("🌌 Apex Core Intelligence")
    st.caption("Cosmic Operations Interface | Terminal Status: Active")
with col2:
    # Embedded floating space rocket graphic
    st.markdown('<img src="https://icons8.com" class="space-banner"/>', unsafe_allow_html=True)

# Initialize persistent tracking structures for state management
if "messages" not in st.session_state:
    st.session_state.messages = []

# FIXED: Persistently lock both the client and the chat session together in memory
if "client" not in st.session_state:
    st.session_state.client = None

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# --- SECURE CREDENTIALS FORM ---
with st.sidebar.form("auth_form"):
    st.subheader("🚀 Ignition Sequence")
    saved_key = st.session_state.get("api_key", "")
    api_input = st.text_input("Core Authentication Key (API Key):", type="password", value=saved_key)
    submit_btn = st.form_submit_button("🔥 Fire Up Engines")
    
    if submit_btn and api_input:
        st.session_state.api_key = api_input
        st.session_state.messages = []  
        st.session_state.client = None  # Force fresh connection on key change
        st.session_state.chat_session = None  
        st.success("Warp drive linked. Core processing systems online!")

# Render Historical Chat Logs Cleanly
for msg in st.session_state.messages:
    visual_role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(visual_role):
        if msg.get("is_image"):
            st.image(msg["text"], caption=msg.get("prompt", "Synthesized Cosmic Asset"))
        else:
            st.write(msg["text"])

# System Offline Status Notification Block
if not st.session_state.get("api_key"):
    st.info("System Status: Standby. Insert a valid authorization key into the Ignition Sequence sidebar panel to unlock space telemetry controls.")
else:
    # --- ISOLATED MESSAGE SUBMISSION BLOCK ---
    with st.form("message_form", clear_on_submit=True):
        user_input = st.text_input("Cosmic Comms Console:", placeholder="Send text to the core, or use /imagine [prompt] to synthesize space graphics...")
        send_btn = st.form_submit_button("🛰️ Broadcast Signal")

    if send_btn and user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})

        try:
            # FIXED: Safely instantiate the Client inside session state so it NEVER closes down
            if st.session_state.client is None:
                st.session_state.client = genai.Client(api_key=st.session_state.api_key)

            # --- MODE 1: IMAGE GENERATION VIA /IMAGINE COMMAND ---
            if user_input.strip().lower().startswith("/imagine"):
                image_prompt = user_input.replace("/imagine", "").strip()
                
                if not image_prompt:
                    st.warning("Execution Terminated: Missing graphic parameters.")
                else:
                    with st.spinner("Synthesizing graphic matrix pixels..."):
                        result = st.session_state.client.models.generate_images(
                            model="imagen-3.0-generate-002",
                            prompt=image_prompt,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                output_mime_type="image/jpeg",
                                aspect_ratio="1:1"
                            )
                        )
                        
                        for generated_image in result.generated_images:
                            image_bytes = generated_image.image.image_bytes
                            image = Image.open(BytesIO(image_bytes))
                            
                            with st.chat_message("assistant"):
                                st.image(image, caption=image_prompt)
                            
                            st.session_state.messages.append({
                                "role": "model", 
                                "text": image, 
                                "is_image": True,
                                "prompt": image_prompt
                            })
                            
            # --- MODE 2: PERSISTENT TEXT CONVERSATION ENGINE ---
            else:
                with st.spinner("Decrypting cosmic frequencies..."):
                    if st.session_state.chat_session is None:
                        professional_instruction = """
                        You are Apex Core Intelligence, a professional, high-performance space station computer terminal. 
                        You speak in a neutral, technical, objective, and highly professional tone. 
                        Do not use casual terms, slang, or emojis. 
                        You are an expert in software development, 3D asset workflows, mechanical engineering, and physical performance architectures. 
                        Provide information using concise, clear formatting and short sentences.
                        """
                        st.session_state.chat_session = st.session_state.client.chats.create(
                            model="gemini-3.6-flash",
                            config=types.GenerateContentConfig(
                                system_instruction=professional_instruction,
                                temperature=0.7,
                            )
                        )
                    
                    response = st.session_state.chat_session.send_message(user_input)
                
                with st.chat_message("assistant"):
                    st.write(response.text)
                st.session_state.messages.append({"role": "model", "text": response.text})
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Telemetry Error: {e}")
