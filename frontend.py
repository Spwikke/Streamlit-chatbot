import streamlit as st
from backend import extraire_texte_pdf, question_gemini

st.set_page_config(
    page_title="PDF ChatBot",
    page_icon="📄",
)

if "texte_pdf" not in st.session_state: 
    st.session_state.texte_pdf = ""
if "messages" not in st.session_state:   # nous permettra de conserver les msg précédents
    st.session_state.messages = []

st.title("Welcome to my chat app !", text_alignment="center")
st.caption("Assistant spécialisé dans l'analyse de PDF", text_alignment="center")
st.divider()

for message in st.session_state.messages:
    if message["role"] == "user":   # Conservation de l'avatar dans l'historique
        avatar = "👤"
    else:
        avatar = "🤖"
    message_chat = st.chat_message(message["role"], avatar=avatar)
    message_chat.write(message["content"])

prompt = st.chat_input(
    "Pose une question ou ajoute un PDF",
    accept_file=True,
    file_type=["pdf"],
)

if prompt and prompt.files:
    fichier = prompt.files[0]
    st.write("PDF chargé :", fichier.name)
    st.session_state.texte_pdf = extraire_texte_pdf(fichier)

    st.success("Un PDF à bien été chargé !")
    st.write("Nombre de caractères :", len(st.session_state.texte_pdf))


if prompt and prompt.text:
    question = prompt.text

    message_chat = st.chat_message("user", avatar="👤")
    message_chat.write(question)
    if st.session_state.texte_pdf:
        message_chat = st.chat_message("assistant", avatar="🤖")
        with message_chat:
            with st.spinner("Analyse du PDF en cours...", show_time=True):
                reponse = question_gemini(question, st.session_state.texte_pdf, st.session_state.messages)
            st.write(reponse)
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": reponse
        })
    else:
        st.warning("Charge d'abord un PDF.")
