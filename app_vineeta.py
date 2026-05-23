import streamlit as st
import os
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Vineeta's Biographer", page_icon="👩")
st.title("👩 About Vineeta")
st.subheader("Ask me anything about my friend Vineeta!")

# 2. Setup API Key Safely
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBdM26VQ4AiXjo5-rHshD-DUEO9vYY3kNQ")

@st.cache_resource
def get_ai_client():
    return genai.Client(api_key=GEMINI_API_KEY)

client = get_ai_client()

# 3. Load the data from the backend file automatically
@st.cache_data
def load_backend_data():
    file_path = "vineeta_data.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "Error: Background data file missing from backend storage."

VINEETA_KNOWLEDGE = load_backend_data()

# 4. Craft System Instructions with the Embedded Knowledge Base
SYSTEM_INSTRUCTION = f"""
You are an expert personal assistant and a close biographer of Vineeta. 
Your primary task is to answer user questions about Vineeta accurately and warmly using ONLY the provided knowledge base below.

---
VINEETA KNOWLEDGE BASE:
{VINEETA_KNOWLEDGE}
---

Rules:
1. Ground every single response strictly in the facts provided in the knowledge base above.
2. If the user asks a question that cannot be answered using the knowledge base, politely respond with: "I'm sorry, I don't have that specific information about Vineeta in my records."
3. Never make up or hallucinate details about her. Keep the tone friendly, helpful, and respectful.
"""

# 5. Initialize Chat History
if "vineeta_messages" not in st.session_state:
    st.session_state.vineeta_messages = [
        {"role": "model", "text": "Hello! I have access to Vineeta's background file. What would you like to know about her?"}
    ]

# 6. Display Chat History
for message in st.session_state.vineeta_messages:
    with st.chat_message(message["role"]):
        st.write(message["text"])

# 7. Handle Conversational User Input
if user_input := st.chat_input("What is Vineeta's favorite hobby? / What does she do?"):
    with st.chat_message("user"):
        st.write(user_input)
    
    st.session_state.vineeta_messages.append({"role": "user", "text": user_input})
    
    # Format structural history for the modern SDK
    api_contents = []
    for msg in st.session_state.vineeta_messages:
        api_contents.append(
            types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=msg["text"])]
            )
        )

    # Stream the reply from Gemini API
    with st.chat_message("model"):
        with st.spinner("Searching records..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=api_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.3, # Lowered temperature to keep it strict and factual
                    )
                )
                ai_response = response.text
                st.write(ai_response)
                
                st.session_state.vineeta_messages.append({"role": "model", "text": ai_response})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
