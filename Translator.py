import streamlit as st
from langchain.schema import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the language model
model = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)

# Define prompt template for translation ONLY
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a translation model. Translate the given text to {language}. Do not engage in conversation or provide any additional information. Only provide the translation.",
        ),
        ("human", "{text}"),  # The text to translate
    ]
)

# Combine prompt with model
translate_chain = prompt | model

# Streamlit App
st.title("Multilingual Translation Tool")
st.write("Translate text to various languages.")

# Sidebar for language selection
st.sidebar.header("Settings")
language = st.sidebar.selectbox(
    "Choose the target language:",
    ["English", "Spanish", "French", "German", "Hindi", "Chinese", "Arabic"]
)

# Input area for user text
user_text = st.text_area("Enter text to translate:")

# Translate button
if st.button("Translate"):
    if user_text.strip():
        try:
            # Invoke the model for translation
            response = translate_chain.invoke({"text": user_text, "language": language})

            # Display the translation
            st.write(f"**Translation ({language}):** {response.content}")

        except Exception as e:  # Catch potential errors during translation
            st.error(f"An error occurred during translation: {e}")
    else:
        st.warning("Please enter text to translate.")