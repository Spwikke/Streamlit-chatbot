import streamlit as st
from backend import creer_agent
from pathlib import Path

st.set_page_config(
    page_title="PDF ChatBot",
    page_icon="📄",
)

if "messages" not in st.session_state:   # nous permettra de conserver les msg précédents
    st.session_state.messages = []

with st.sidebar:
    st.title("Mes documents")
    fichiers = st.file_uploader(
        "Ajouter des PDF",
        type=["pdf"],
        accept_multiple_files=True
    )
    dossier_pdf = Path("pdfs")
    dossier_pdf.mkdir(exist_ok=True)
    if fichiers:
        for fichier in fichiers:
            chemin = dossier_pdf / Path(fichier.name).name
            chemin.write_bytes(fichier.getvalue())
        st.divider()
    st.subheader("Documents chargés")
    for chemin in dossier_pdf.glob("*.pdf"):
        st.write("📄", chemin.name)

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
    st.chat_message("user", avatar="👤").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    agent = creer_agent()
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("L'agent réfléchit..."):
            resultat = agent.invoke({
                "messages": st.session_state.messages
            })
            reponse = resultat["messages"][-1].text
        st.write(reponse)
    st.session_state.messages.append({
        "role": "assistant",
        "content": reponse
    })
