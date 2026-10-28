import streamlit as st
from backend import extraire_texte_pdf, question_gemini, choisir_document

st.set_page_config(
    page_title="PDF ChatBot",
    page_icon="📄",
)

if "texte_pdf" not in st.session_state: 
    st.session_state.texte_pdf = ""
if "messages" not in st.session_state:   # nous permettra de conserver les msg précédents
    st.session_state.messages = []
if "fichiers_pdf" not in st.session_state:
    st.session_state.fichiers_pdf = {}

with st.sidebar:
    st.title("Mes documents")
    fichiers = st.file_uploader(
        "Ajouter des PDF",
        type=["pdf"],
        accept_multiple_files=True
    )
    if fichiers:
        for fichier in fichiers:
            st.session_state.fichiers_pdf[fichier.name] = fichier.getvalue()
        st.divider()
    st.subheader("Documents chargés")
    for nom in st.session_state.fichiers_pdf:
        st.write("📄", nom)

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

prompt = st.chat_input("Pose une question")

if prompt:
    question = prompt
    message_chat = st.chat_message("user", avatar="👤")
    message_chat.write(question)
    if st.session_state.fichiers_pdf:
        message_chat = st.chat_message("assistant", avatar="🤖")
        with message_chat:
            with st.spinner("Recherche du document...", show_time=True):
                noms_fichiers = list(st.session_state.fichiers_pdf.keys())
                nom_choisi = choisir_document(question, noms_fichiers)
            if nom_choisi is None:
                texte_pdf = ""
                st.info("Aucun PDF pertinent, réponse avec les connaissances de Gemini.")
            else:
                st.write("PDF sélectionné :", nom_choisi)
                texte_pdf = extraire_texte_pdf(
                    st.session_state.fichiers_pdf[nom_choisi]
                )
                st.success("Le PDF sélectionné a bien été analysé !")
                st.write("Nombre de caractères :", len(texte_pdf))
            with st.spinner("Génération de la réponse...", show_time=True):
                reponse = question_gemini(
                    question, texte_pdf, st.session_state.messages
                )
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
        with st.spinner("Génération de la réponse...", show_time=True):
            reponse = question_gemini(
            question, "", st.session_state.messages
        )
    st.chat_message("assistant", avatar="🤖").write(reponse)
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": reponse})
