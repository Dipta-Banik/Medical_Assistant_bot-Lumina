import streamlit as st
from datetime import datetime
import time
from bot_logic import handle_query
from doctor import doctor_info
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LUMINA_AVATAR = os.path.join(BASE_DIR, '..', 'png', 'Avatar.png')
USER_AVATAR = os.path.join(BASE_DIR, '..', 'png', 'user.png')


st.set_page_config(page_title="Lumina - Medical Chatbot", page_icon="🩺", layout="wide")
st.markdown("""
    <style>
    .block-container {
        padding: 1.5rem 2rem;
    }
    .stChatMessage {
        margin-bottom: 0.5rem;
    }
    .chat-title {
        font-weight: 700;
        font-size: 1.2rem;
        color: #2d2d2d;
        margin-bottom: 0.5rem;
    }
    .user-msg .stMarkdown {
        background-color: #e1f5fe;
        padding: 10px;
        border-radius: 12px;
    }
    .bot-msg .stMarkdown {
        background-color: #fff8e1;
        padding: 10px;
        border-radius: 12px;
    }
    .quick-buttons {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .quick-buttons button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.image("/Users/diptabanik/Desktop/Medical_chatbot/png/Lumina_logo.png", width=200)
    st.markdown("## 👩‍⚕️ Lumina - Medical Assistant")
    st.markdown("""
        Hi, I'm **Lumina**, your smart healthcare assistant 🤖  
        I can help you:
        - 🔍 Find doctors  
        - 🏥 Show departments  
        - 📅 Book appointments  
        - 🚑 Handle emergencies
    """)
    st.markdown("### 💬 Quick Options")
    
    with st.container():
        if st.button("🧑‍⚕️ Find Doctor"):
            st.session_state.chat_history.append(("You", "Find doctor"))
            response = doctor_info()
            time.sleep(0.8)
            st.session_state.chat_history.append(("Lumina", response))
            st.rerun()

        if st.button("🏥 Department Info"):
            st.session_state.chat_history.append(("You", "Show departments"))
            response = handle_query("Show departments")
            time.sleep(0.8)
            st.session_state.chat_history.append(("Lumina", response))
            st.rerun()

        if st.button("📅 Book Appointment"):
            st.session_state.chat_history.append(("You", "Book appointment"))
            response = handle_query("Book appointment")
            time.sleep(0.8)
            st.session_state.chat_history.append(("Lumina", response))
            st.rerun()

def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning!"
    elif 12 <= hour < 17:
        return "Good afternoon!"
    else:
        return "Good evening!"

time_greeting = get_greeting()
Lumina_intro = f"Hi, {time_greeting} I'm Lumina, your medical assistant. How may I help you today?"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("Lumina", Lumina_intro)
    ]

for sender, message in st.session_state.chat_history:
    if sender == "Lumina":
        avatar = LUMINA_AVATAR
        role = "assistant"
    else:  # sender == "You"
        avatar = USER_AVATAR
        role = "user"

    with st.chat_message(role, avatar=avatar):
        if sender == "Lumina" and message == Lumina_intro:
            st.markdown("#### 👩‍⚕️ Lumina", unsafe_allow_html=True)

        bubble_class = "user-msg" if sender == "You" else "bot-msg"
        st.markdown(
            f"<div class='{bubble_class}'><strong>{sender if sender == 'You' else ''}</strong><br>{message}</div>",
            unsafe_allow_html=True
        )

user_query = st.chat_input("Type your message here...")

if user_query:
    st.session_state.chat_history.append(("You", user_query))
    with st.chat_message("user"):
        st.markdown(f"<div class='user-msg'><strong>You:</strong><br>{user_query}</div>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("Lumina is typing..."):
            time.sleep(1.5)
            response = handle_query(user_query)
        st.markdown(f"""
<div style="
    color: 7FFFD4;
    font-family: 'Poppins', sans-serif;
    line-height: 2;
    font-size: 16px;
">
    <strong style="color: 9400D3;">👩‍⚕️ Lumina:</strong><br>
    {response}
</div>
""", unsafe_allow_html=True)

    st.session_state.chat_history.append(("Lumina", response))
    
    
