import streamlit as st
#from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv())

pages = {
    "Pagina principale": [st.Page("main_page.py", title="Guardian")],
    "Caricamento immagini": [st.Page("pic_page.py", title="Carica immagine")],
}

pg = st.navigation(pages)
pg.run()