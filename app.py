import streamlit as st
from google import genai
from google.genai import types
from io import BytesIO
from PIL import Image

# Set professional layout with a sharp tech icon
st.set_page_config(page_title="Apex AI", page_icon="⚙️", layout="centered")

st.title("⚙️ Apex Core Intelligence")
st.caption("Custom Core Framework | Powered by Gemini 3.6 & Imagen 3")

# Initialize persistent session tracking structures
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AUTHORIZATION SIDEBAR BLOCK ---
with st.sidebar.form("auth_form"):
    st.subheader("⚡ Ignition Vault")
    saved_key = st.session_state.get("api_key", "")
    api_input = st.text_input("Plug In Your Core Key (API Key):", type="password", value=saved_key)
    submit_btn = st.form_submit_button("🔥 Boot the Core")
    
    if submit_btn and api_input:
        st.session_state.api_key = api_input
        st.session_state.messages = [] # Clear history on fresh token login
        st.success("Core link established. Systems are fully locked and loaded, bro!")

# Render History Blocks Cleanly
for msg in st.session_state.messages:
    visual_role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(visual_role):
        if msg.get("is_image"):
            st.image(msg["text"], caption=msg.get("prompt", "Rendered Asset"))
        else:
            st.write(msg["text"])

# Creative Standby Notification if the engine isn't fueled yet
if not st.session_state.get("api_key"):
    st.info("Core Engine is offline, bro. Drop your access key into the Ignition Vault on the left sidebar and smash 'Boot the Core' to wake it up!")
else:
    # --- ISOLATED MESSAGE SUBMISSION BLOCK ---
    with st.form("message_form", clear_on_submit=True):
        user_input = st.text_input("Command Console:", placeholder="Type a message, or fire up /imagine [prompt] to synthesize 3D art...")
        send_btn = st.form_submit_button("🚀 Run Command")

    if send_btn and user_input:
        # Append User text directly to local history cache
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})

        try:
            # Initialize the global Gemini Client strictly in Developer Mode
            client = genai.Client(apiKey=st.session_state.api_key)

            # --- MODE 1: IMAGE GENERATION VIA /IMAGINE COMMAND ---
            if user_input.strip().lower().startswith("/imagine"):
                image_prompt = user_input.replace("/imagine", "").strip()
                
                if not image_prompt:
                    st.warning("You forgot the prompt, bro! Give me something to render after the /imagine command.")
                else:
                    with st.spinner("Apex image engine is cooking pixels in the lab..."):
                        # Calling the verified developer-tier image engine model
                        result = client.models.generate_images(
                            model="imagen-3.0-generate-002",
                            prompt=image_prompt,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                output_mime_type="image/jpeg",
                                aspect_ratio="1:1"
                            )
                        )
                        
                        # Process bytes directly into an image object
                        for generated_image in result.generated_images:
                            image_bytes = generated_image.image.image_bytes
                            image = Image.open(BytesIO(image_bytes))
                            
                            # Render instantly in chat layout
                            with st.chat_message("assistant"):
                                st.image(image, caption=image_prompt)
                            
                            # Cache the image data into local state tracking
                            st.session_state.messages.append({
                                "role": "model", 
                                "text": image, 
                                "is_image": True,
                                "prompt": image_prompt
                            })
                            
            # --- MODE 2: STANDARD TEXT CHAT CONVERSATION ---
            else:
                with st.spinner("Apex processor compiling data logs..."):
                    # Format previous history strings matching strict developer tags
                    history_logs = []
                    for m in st.session_state.messages[:-1]:
                        if m.get("is_image"):
                            continue
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
            
            # Force layout execution refresh step to keep visual order crisp
            st.rerun()
            
        except Exception as e:
            st.error(f"System Glitch: {e}")
