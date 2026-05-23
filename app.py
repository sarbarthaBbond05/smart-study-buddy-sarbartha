import streamlit as str
from google import genai
from google.genai import types

# 1. Page Configuration
str.set_page_config(page_title="Smart Study Buddy", page_icon="🎓")
str.title("🎓 Smart Study Buddy")
str.subheader("Your AI tutor that simplifies complex topics!")

# 2. Setup API Key (Enter your key here)
GEMINI_API_KEY = "AIzaSyADnqhgDHekY2IlzKzPZIR1Z4sd4bgoXpg"

# Initialize the Gemini Client
@str.cache_resource
def get_ai_client():
    return genai.Client(api_key=GEMINI_API_KEY)

client = get_ai_client()

# 3. System Instructions (The "Persona" or Prompt Engineering)
SYSTEM_INSTRUCTION = """
You are an elite, patient, and encouraging AI Math and Science tutor named "Study Buddy".
Your job is to explain complex concepts in an incredibly simple, intuitive way—as if you are explaining it to a 10-year-old.
Use analogies, fun examples, and formatting (like bullet points) to break down information. 
At the end of your explanation, always ask a quick, fun follow-up question to test the user's understanding.
"""

# 4. Initialize Chat History in Session State (so the app remembers previous messages)
if "messages" not in str.session_state:
    str.session_state.messages = [
        {"role": "model", "text": "Hi there! I'm your Study Buddy created by Sarbartha. What difficult topic can I help you understand today?"}
    ]

# 5. Display Chat History
for message in str.session_state.messages:
    with str.chat_message(message["role"]):
        str.write(message["text"])

# 6. Handle User Input
if user_input := str.chat_input("Ask me to explain any concept..."):
    # Display user message in chat message container
    with str.chat_message("user"):
        str.write(user_input)
    
    # Add user message to session history
    str.session_state.messages.append({"role": "user", "text": user_input})
    
    # Format the entire history into contents the API expects
    api_contents = []
    for msg in str.session_state.messages:
        # Convert "model" role to "model" and "user" to "user" 
        # (Gemini API expects 'user' or 'model')
        api_contents.append(
            types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=msg["text"])]
            )
        )

    # Call the Gemini API
    with str.chat_message("model"):
        with str.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=api_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                ai_response = response.text
                str.write(ai_response)
                
                # Add AI response to session history
                str.session_state.messages.append({"role": "model", "text": ai_response})
                
            except Exception as e:
                str.error(f"An error occurred: {e}")