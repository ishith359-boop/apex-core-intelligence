import streamlit as st
from google import genai
from google.genai import types
from io import BytesIO
from PIL import Image

# Initialize production interface configurations
st.set_page_config(page_title="Apex Systems", page_icon="⚙️", layout="centered")

st.title("⚙️ Apex Core Intelligence")
st.caption("Secure Developer Terminal | Model Status: Active")

# Initialize persistent tracking structures for state management
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# --- SECURE CREDENTIALS FORM ---
with st.sidebar.form("auth_form"):
    st.subheader("🔒 System Authentication")
    saved_key = st.session_state.get("api_key", "")
    api_input = st.text_input("Developer Authorization Token (API Key):", type="password", value=saved_key)
    submit_btn = st.form_submit_button("Initialize Engine")
    
    if submit_btn and api_input:
        st.session_state.api_key = api_input
        st.session_state.messages = []  # Reset thread on new initialization
        st.session_state.chat_session = None  # Clear active session cache
        st.success("Authorization token verified. System initialized successfully.")

# Render Historical Chat Logs Cleanly
for msg in st.session_state.messages:
    visual_role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(visual_role):
        if msg.get("is_image"):
            st.image(msg["text"], caption=msg.get("prompt", "Generated Data Asset"))
        else:
            st.write(msg["text"])

# System Offline Status Notification Block
if not st.session_state.get("api_key"):
    st.info("System Status: Offline. Please insert a valid developer authorization token in the authentication panel to unlock terminal operations.")
else:
    # --- ISOLATED MESSAGE SUBMISSION BLOCK ---
    with st.form("message_form", clear_on_submit=True):
        user_input = st.text_input("Terminal Command:", placeholder="Enter computational command or use /imagine [prompt] for asset generation...")
        send_btn = st.form_submit_button("Execute Command")

    if send_btn and user_input:
        # Append query natively to thread logs
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})

        try:
            # Initialize Developer-tier GenAI client
            client = genai.Client(api_key=st.session_state.api_key)

            # --- MODE 1: NATIVE DEVELOPER-TIER IMAGE GENERATION ---
            if user_input.strip().lower().startswith("/imagine"):
                image_prompt = user_input.replace("/imagine", "").strip()
                
                if not image_prompt:
                    st.warning("Execution Halted: Prompt missing for generation command.")
                else:
                    with st.spinner("Processing image generation request..."):
                        result = client.models.generate_images(
                            model="imagen-3.0-generate-002",
                            prompt=image_prompt,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                output_mime_type="image/jpeg",
                                aspect_ratio="1:1"
                            )
                        )
                        
                        # Process image bytes output safely
                        for generated_image in result.generated_images:
                            image_bytes = generated_image.image.image_bytes
                            image = Image.open(BytesIO(image_bytes))
                            
                            # Render directly in the active application window
                            with st.chat_message("assistant"):
                                st.image(image, caption=image_prompt)
                            
                            # Append structural tracking values into session state logs
                            st.session_state.messages.append({
                                "role": "model", 
                                "text": image, 
                                "is_image": True,
                                "prompt": image_prompt
                            })
                            
            # --- MODE 2: PERSISTENT TEXT CONVERSATION ENGINE ---
            else:
                with st.spinner("Compiling neural framework data..."):
                    # Instantiating the client chat object ONCE to prevent enterprise platform tracking crashes
                    if st.session_state.chat_session is None:
                        professional_instruction = """
                        You are Apex Core Intelligence, a professional, high-performance AI collaborator. 
                        You speak in a neutral, technical, objective, and highly professional tone. 
                        Do not use casual terms, slang, or emojis. 
                        You are an expert in software development, 3D asset workflows, mechanical engineering, and physical performance architectures. 
                        Provide information using concise, clear formatting and short sentences.
                        """
                        st.session_state.chat_session = client.chats.create(
                            model="gemini-3.6-flash",
                            config=types.GenerateContentConfig(
                                system_instruction=professional_instruction,
                                temperature=0.7,
                            )
                        )
                    
                    # Core Developer-tier message request passing
                    response = st.session_state.chat_session.send_message(user_input)
                
                with st.chat_message("assistant"):
                    st.write(response.text)
                st.session_state.messages.append({"role": "model", "text": response.text})
            
            # Refresh layout pipeline cleanly to maintain alignment
            st.rerun()
            
        except Exception as e:
            st.error(f"System Execution Glitch: {e}")
