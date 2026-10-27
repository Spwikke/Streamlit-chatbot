import streamlit as st
import numpy as np
import pymupdf

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
    document.close()
    st.write("Texte extrait du PDF :")
    st.write(texte)










