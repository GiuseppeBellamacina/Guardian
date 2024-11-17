import streamlit as st

pages = {
    "Pagina principale": [st.Page("main_page.py", title="Guardian")],
    "Caricamento immagini": [st.Page("pic_page.py", title="Carica immagine")],
}

pg = st.navigation(pages)
pg.run()