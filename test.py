# python -m pip install streamlit
# python -m streamlit run test.py -> une app streamlit doit être lancée avec cette cmd

import streamlit as st
import numpy as np

message = st.chat_message("human", avatar="🦖")
message.write("Welcome to my chat app 👋")
