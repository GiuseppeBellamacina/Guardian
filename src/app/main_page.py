import streamlit as st
import os
import asyncio
from chatbot.graph import *
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from chatbot.graph import (
    calculate_risk_coefficients,
    car_analysis,
    go_to_searcher,
    State,
    compile_graph
)
from chatbot.guardian import Guardian, PictureAnalyzer
from chatbot.query_generator import create_query_generator
from chatbot.caller import Caller
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from uuid import uuid4

DB = Neo4jGraph(
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"]
)

def generate_thread_id():
    return str(uuid4())

def compile_guardian(session_id: str):
    global DB
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=st.secrets["OPENAI_API_KEY"]
    )
    picture_analysis = PictureAnalyzer(llm).create_picture_analyzer()
    query_gen = create_query_generator(llm, DB)
    guardian = Guardian(llm, [go_to_searcher])
    llm_with_guardian = guardian.create_guardian()
    search_node = ToolNode([go_to_searcher])
    tool_node = ToolNode([calculate_risk_coefficients, car_analysis])
    
    mini_llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )
    
    caller = Caller(mini_llm, [calculate_risk_coefficients,car_analysis]).create_caller()
    
    app_tools = {
        'db': DB,
        'caller': caller,
        'guardian': llm_with_guardian,
        'cypher': query_gen,
        'picture': picture_analysis
    }
    
    config = {"configurable": {"thread_id": session_id}, "recursion_limit": 15}
    config['configurable'].update(app_tools)
    
    graph = StateGraph(State)
    memory = MemorySaver()
    app = compile_graph(graph, memory, search_node, tool_node)
    return app, config

def initialize_session_state():
    if "is_initialized" not in st.session_state or not st.session_state.is_initialized:
        st.session_state.is_initialized = False
        print("\33[1;36m[Session]\33[0m: Avvio inizializzazione")
        
        st.session_state.session_id = generate_thread_id()
        
        # Messaggi
        st.session_state.messages = []
        print("\33[1;32m[Session]\33[0m: Messaggi inizializzati")

        st.session_state.has_uploaded_picture = False

        app, config = compile_guardian(st.session_state.session_id)
        st.session_state.model = app
        st.session_state.config = config
        st.session_state.snap = None
        print("\33[1;32m[Session]\33[0m: Modello e config inizializzati")

        st.session_state.is_initialized = True
        print("\33[1;32m[Session]\33[0m: Inizializzazione completata")
        return st.session_state.is_initialized

def update_session():
    if "is_initialized" not in st.session_state or not st.session_state.is_initialized:
        print("\33[1;31m[Session]\33[0m: Sessione non inizializzata")
        raise Exception(RuntimeError)

    with st.sidebar:
        st.write(" ")
        if st.button("Clear", use_container_width=True):
            st.session_state.messages = []
            app, config = compile_guardian(st.session_state.session_id)
            st.session_state.model = app
            st.session_state.config = config
            st.session_state.snap = None
            print("\33[1;32m[Session]\33[0m: Sessione ripulita")
            st.success("Session cleared")
    
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            
    with st.container():
        if st.session_state.messages:
            col_index = None
            button_queries = ["Dammi tutti i dettagli sui suoi figli",
                              "Dammi tutti i dettagli sul suo partner",
                              "Dammi tutti i dettagli sulla sua auto"]
            cols = st.columns(3)
            with cols[0]:
                if st.button("Info sui figli", use_container_width=True):
                    col_index = 0
            with cols[1]:
                if st.button("Info sul partner", use_container_width=True):
                    col_index = 1
            with cols[2]:
                if st.button("Info sull'auto", use_container_width=True):
                    col_index = 2
            if col_index:
                asyncio.run(conversation(button_queries[col_index]))
    if prompt := st.chat_input("Inserisci i dettagli della tua query", key="first_question"):
        os.system("cls" if os.name == "nt" else "clear")
        asyncio.run(conversation(prompt))

async def conversation(prompt):
    st.session_state.messages.append({
                "role": "human",
                "content": prompt
            })
    with st.chat_message("human"):
        st.markdown(prompt)

    response = None
    with st.chat_message("ai"):
        containers = (st.empty(), st.empty())
        with st.spinner("Elaborazione in corso..."):
            events = st.session_state.model.astream(
                {"messages": ("user", prompt), "is_picture": False}, config=st.session_state.config, stream_mode="values",
            )
            async for event in events:
                final_message = event
            response = final_message['messages'][-1]
            st.session_state.snap = st.session_state.model.get_state(st.session_state.config).values
    
    st.session_state.messages.append({
                "role": "ai",
                "content": response.content,
                "response_time": ""
            })
            
    st.rerun()
    
def main():
    st.set_page_config(page_icon="👮‍♂️", page_title="Guardian")
    st.title("Guardian👮‍♂️")
    st.subheader("L'assistente per strade più sicure")
    account1 = '[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label=Drake9098&color=orange)](https://github.com/Drake9098)'
    account2 = '[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label=GiuseppeBellamacina&color=blue)](https://github.com/GiuseppeBellamacina)'
    st.markdown(account1 + " " + account2,unsafe_allow_html=True)

    initialize_session_state()
    update_session()


main()
