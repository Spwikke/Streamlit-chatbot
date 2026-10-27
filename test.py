import streamlit as st
import numpy as np

message = st.chat_message("human", avatar="🦖")
message.write("Welcome to my chat app 👋")

prompt = st.chat_input(
    "Say something and/or attach an image",
    accept_file=True,
    file_type=["pdf"],
)
if prompt and prompt.text:
    st.markdown(prompt.text)
if prompt and prompt.files:
    fichier = prompt.files[0]
    st.write(fichier.name)












