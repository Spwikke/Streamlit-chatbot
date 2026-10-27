import streamlit as st
import numpy as np
import pymupdf

if "texte_pdf" not in st.session_state: 
    st.session_state.texte_pdf = ""

message = st.chat_message("human", avatar="🦖")
message.write("Welcome to my chat app 👋")

prompt = st.chat_input(
    "Say something and/or attach an image",
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

if prompt and prompt.text:
    question = prompt.text
    st.write("Question posée :", question)
    if not st.session_state.texte_pdf:
        st.warning("Veuillez charger un PDF.")

if st.session_state.texte_pdf:
    st.success("Un PDF à bien été chargé !")
    st.write("Nombre de caractères :", len(st.session_state.texte_pdf))









