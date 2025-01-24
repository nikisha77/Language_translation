import streamlit as st
from langchain.schema import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import easyocr
from PIL import Image
import numpy as np
import io
import tempfile
import shutil
from PyPDF2 import PdfReader
from docx import Document

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


model = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a translation model. Translate the given text to {language}. Do not engage in conversation or provide any additional information. Only provide the translation.",
        ),
        ("human", "{text}"),
    ]
)

translate_chain = prompt | model

reader = easyocr.Reader(['en'])

st.title("Multilingual Translation Tool")
st.write("Translate text to various languages.")

st.sidebar.header("Settings")
language = st.sidebar.selectbox(
    "Choose the target language:",
    ["English", "Spanish", "French", "German", "Hindi", "Chinese", "Arabic"]
)

uploaded_file = st.file_uploader("Upload a text file or an image", type=["txt", "pdf", "docx", "jpg", "jpeg", "png"])

def extract_text_from_image(image):
    image_bytes = io.BytesIO(image.read())
    pil_image = Image.open(image_bytes)
    image_np = np.array(pil_image)
    result = reader.readtext(image_np)
    text = " ".join([res[1] for res in result])
    return text

def extract_text_from_file(file):
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.name)
    
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    
    text = ""
    file_type = file.type

    if file_type == "text/plain":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    elif file_type == "application/pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text()
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])

    shutil.rmtree(temp_dir)
    
    return text

user_text = st.text_area("Or, you can enter text directly:")

if uploaded_file:
    if uploaded_file.type.startswith("image/"):
        extracted_text = extract_text_from_image(uploaded_file)
        st.write("Extracted text from image:")
        st.text_area("Text from image", extracted_text, height=200)
        user_text = extracted_text
    else:
        extracted_text = extract_text_from_file(uploaded_file)
        st.write("Extracted text from file:")
        st.text_area("Text from file", extracted_text, height=200)
        user_text = extracted_text

if st.button("Translate"):
    if user_text.strip():
        try:
            response = translate_chain.invoke({"text": user_text, "language": language})
            st.write(f"**Translation ({language}):** {response.content}")
        except Exception as e:
            st.error(f"An error occurred during translation: {e}")
    else:
        st.warning("Please enter text to translate.")
