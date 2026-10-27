import streamlit as st
import pymupdf
import os
from google import genai

st.set_page_config(
    page_title="PDF ChatBot",
    page_icon="📄",
)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

if "texte_pdf" not in st.session_state: 
    st.session_state.texte_pdf = ""

st.title("Welcome to my chat app !", text_alignment="center")
st.caption("Assistant spécialisé dans l'analyse de PDF", text_alignment="center")
st.divider()

prompt = st.chat_input(
    "Pose une question ou ajoute un PDF",
    accept_file=True,
    file_type=["pdf"],
)

if prompt and prompt.files:
    fichier = prompt.files[0]
    st.write("PDF chargé :", fichier.name)
    document = pymupdf.open(         # ouvre les données comme un document PDF
        stream=fichier.getvalue(),   # récupère les données binaires du fichier envoyé à Streamlit
        filetype="pdf"  
    )
    texte = ""
    for page in document:
        texte += page.get_text()
    st.session_state.texte_pdf = texte   # permet de conserver des données entre les interactions
    document.close()

if st.session_state.texte_pdf:
    st.success("Un PDF à bien été chargé !")
    st.write("Nombre de caractères :", len(st.session_state.texte_pdf))

if prompt and prompt.text:
    question = prompt.text
    message = st.chat_message("user", avatar="👤")
    message.write(question)
    if st.session_state.texte_pdf:
        instructions = f"""
        Réponds uniquement à partir du document suivant.
        Si la réponse n'est pas présente dans le document, 
        indique que tu ne trouves pas cette information.
        DOCUMENT :
        {st.session_state.texte_pdf}
        QUESTION :
        {question}
        """
        response = client.models.generate_content(
            model = "gemini-3.5-flash-lite",
            contents = instructions
        )
        message = st.chat_message("assistant", avatar="🤖")
        st.write(response.text)
    else:
        st.warning("Charge d'abord un PDF.")


