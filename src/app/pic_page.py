import streamlit as st
import base64
import asyncio

async def call(image):
    events = st.session_state.model.astream(
        {"messages": ("user", image), "is_picture": True}, config=st.session_state.config, stream_mode="values",
    )
    async for event in events:
        final_message = event
    response = final_message['messages'][-1]
    st.session_state.snap = st.session_state.model.get_state(st.session_state.config).values
    return response

st.set_page_config(page_icon="👮‍♂️", page_title="Guardian")
st.title("Caricamento immagini")

cols = st.columns(2, gap="large")
with cols[0]:
    uploaded_picture = st.file_uploader("Carica un'immagine", type=["jpg", "jpeg", "png"])

with cols[1]:
    camera_picture = st.camera_input("Scatta una foto")

if uploaded_picture or camera_picture:
    st.session_state.has_uploaded_picture = True
    st.image(uploaded_picture, caption="Immagine caricata, il modello sta elaborando le informazioni...")
    image_data = uploaded_picture.getvalue()
    image_data = base64.b64encode(image_data).decode("utf-8")
    image = f"{image_data}"

    response = asyncio.run(call(image))
    st.write(response.content)
    st.session_state.has_uploaded_picture = False
    st.session_state.messages.append({
        "role": "ai",
        "content": response.content
    })

    if uploaded_picture:  
        uploaded_picture = None
    else:
        camera_picture = None