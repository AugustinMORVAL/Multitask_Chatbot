import streamlit as st
from app import UIComponents
from config import load_config

config = load_config()
ui = UIComponents(config)

st.set_page_config(page_title="Database", page_icon="img/logo-Cyy6uKYt.png", layout="wide")

st.title("Database")

#Sidebar
st.sidebar.subheader("Connect to an external database")
st.sidebar.button("Connect")
st.sidebar.subheader("Add your own file to the database")
ui.create_file_uploader(sidebar=True)

# Database 
ui.display_database()
