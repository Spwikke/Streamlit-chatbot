import streamlit as st  # pour créer l'interface web 
from backend import creer_agent
from pathlib import Path    # manipuler les chemins et les fichiers

st.set_page_config(
    page_title="PDF ChatBot",
    page_icon="📄",
)

if "messages" not in st.session_state:   # nous permettra de conserver les msg précédents
    st.session_state.messages = []       # session_state permet de conserver les données entre les intéractions

with st.sidebar:
    st.title("Mes documents")
    fichiers = st.file_uploader(
        "Ajouter des PDF",
        type=["pdf"],
        accept_multiple_files=True
    )
    dossier_pdf = Path("pdfs")     # définis le dossier dans lequel seront enregistrés les PDF
    dossier_pdf.mkdir(exist_ok=True)    # on le crée si il n'existe pas encore
    if fichiers:
        for fichier in fichiers:
            chemin = dossier_pdf / Path(fichier.name).name  # pour chaque fichier importé, on construit le chemin du PDF dans le dossier pdfs
            chemin.write_bytes(fichier.getvalue())  # enregistre le contenu du PDF sur le disque dur
        st.divider()
    st.subheader("Documents chargés")
    for chemin in dossier_pdf.glob("*.pdf"):    # parcourt tous les PDF du dossier pdfs
        st.write("📄", chemin.name)

st.title("Welcome to my chat app !", text_alignment="center")
st.caption("Assistant spécialisé dans l'analyse de PDF", text_alignment="center")
st.divider()

for message in st.session_state.messages:   # on réaffiche tous les msg précedents
    if message["role"] == "user":   # on conserve le bon avatar
        avatar = "👤"
    else:
        avatar = "🤖"
    message_chat = st.chat_message(message["role"], avatar=avatar)
    message_chat.write(message["content"])

prompt = st.chat_input("Pose une question") # crée la zone d'input

if prompt:
    st.chat_message("user", avatar="👤").write(prompt)  # affiche la question
    st.session_state.messages.append({"role": "user", "content": prompt})   # on l'ajoute à l'historique
    agent = creer_agent()   # on crée l'agent LangChain
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("L'agent réfléchit..."):
            resultat = agent.invoke({
                "messages": st.session_state.messages   # envoie tout l'historique à l'agent
            })
            reponse = resultat["messages"][-1].text     # récupère le texte de la dernière réponse de l'agent
        st.write(reponse)
    st.session_state.messages.append({
        "role": "assistant",                    # enregsitre la réponse dans l'historique
        "content": reponse
    })
